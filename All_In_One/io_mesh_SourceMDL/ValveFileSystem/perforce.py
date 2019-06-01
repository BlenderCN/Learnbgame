
from __future__ import with_statement

import os
import re
import sys
import time
import marshal
import datetime
import subprocess
import tempfile

from .path import *
from .valve import *
from . import path

from .misc import iterBy

class FinishedP4Operation(Exception): pass
class TimedOutP4Operation(Exception): pass
class P4Exception(Exception): pass

def _p4fast( *args ):
	workingDir = None
	if 'VGAME' in os.environ:
		workingDir = os.path.dirname( os.path.expandvars( '%VGAME%' ) )

	p = subprocess.Popen( 'p4 -G '+ ' '.join( args ), cwd=workingDir, shell=True, stdout=subprocess.PIPE )

	results = []
	try:
		while True:
			results.append( marshal.loads( p.stdout.read() ) )
	except EOFError: pass

	p.wait()

	return results


class P4Output(dict):
	EXIT_PREFIX = 'exit:'
	ERROR_PREFIX = 'error:'

	#
	START_DIGITS = re.compile( '(^[0-9]+)(.*)' )
	END_DIGITS = re.compile( '(.*)([0-9]+$)' )

	def __init__( self, outStr, keysColonDelimited=False ):
		EXIT_PREFIX = self.EXIT_PREFIX
		ERROR_PREFIX = self.ERROR_PREFIX

		self.errors = []

		if isinstance( outStr, str ):
			lines = outStr.split( '\n' )
		elif isinstance( outStr, (list, tuple) ):
			lines = outStr
		else:
			print (outStr)
			raise P4Exception( "unsupported type (%s) given to %s" % (type( outStr ), self.__class__.__name__) )

		delimiter = (' ', ':')[ keysColonDelimited ]
		for line in lines:
			line = line.strip()

			if not line:
				continue

			if line.startswith( EXIT_PREFIX ):
				break
			elif line.startswith( ERROR_PREFIX ):
				self.errors.append( line )
				continue

			idx = line.find( delimiter )
			if idx == -1:
				prefix = line
				data = True
			else:
				prefix = line[ :idx ].strip()
				data = line[ idx + 1: ].strip()
				if data.isdigit():
					data = int( data )

			if keysColonDelimited:
				prefix = ''.join( [ (s, s.capitalize())[ n ] for n, s in enumerate( prefix.lower().split() ) ] )
			else:
				prefix = prefix[ 0 ].lower() + prefix[ 1: ]

			self[ prefix ] = data

		#finally, if there are prefixes which have a numeral at the end, strip it and pack the data into a list
		multiKeys = {}
		for k in self.keys():
			m = self.END_DIGITS.search( k )
			if m is None:
				continue

			prefix, idx = m.groups()
			idx = int( idx )

			data = self.pop( k )
			try:
				multiKeys[ prefix ].append( (idx, data) )
			except KeyError:
				multiKeys[ prefix ] = [ (idx, data) ]

		for prefix, dataList in multiKeys.iteritems():
			try:
				self.pop( prefix )
			except KeyError: pass

			dataList.sort()
			self[ prefix ] = [ d[ 1 ] for d in dataList ]
	def __unicode__( self ):
		return self.__str__()
	def __getattr__( self, attr ):
		return self[ attr ]
	def asStr( self ):
		if self.errors:
			return '\n'.join( self.errors )

		return '\n'.join( '%s:  %s' % items for items in self.iteritems() )


INFO_PREFIX_RE = re.compile( '^info([0-9]*): ' )

def _p4run( *args ):
	if not path.P4File.USE_P4:
		return False

	global INFO_PREFIX_RE
	if '-s' not in args:  #if the -s flag is in the global flags, perforce sends all data to the stdout, and prefixes all errors with "error:"
		args = ('-s',) + args

	workingDir = None
	if 'VGAME' in os.environ:
		workingDir = os.path.dirname( os.path.expandvars( '%VGAME%' ) )

	cmdStr = 'p4 '+ ' '.join( map( str, args ) )
	with tempfile.TemporaryFile() as tmpFile:
		try:
			p4Proc = subprocess.Popen( cmdStr, cwd=workingDir, shell=True, stdin=subprocess.PIPE, stdout=tmpFile.fileno(), stderr=subprocess.PIPE )
		except OSError as detail:
			print ('_p4un: Disabling Perforce due to OSError:', detail)
			path.P4File.USE_P4 = False
			return False

		p4Proc.wait()
		tmpFile.seek( 0 )

		return [ INFO_PREFIX_RE.sub( '', line ) for line in tmpFile.readlines() ]


def p4run( *args, **kwargs ):
	ret = _p4run( *args )
	if ret is False:
		return False

	return P4Output( ret, **kwargs )


P4INFO = None
def p4Info():
	global P4INFO

	if P4INFO:
		return P4INFO

	P4INFO = p4run( 'info', keysColonDelimited=True )
	if not P4INFO:
		path.P4File.USE_P4 = False

	return P4INFO


def populateChange( change ):
		changeNum = change[ 'change' ]
		if isinstance( changeNum, int ) and changeNum:
			fullChange = P4Change.FetchByNumber( changeNum )
			for key, value in fullChange.iteritems():
				change[ key ] = value

class P4ConfigFile( object ):
	'''
	Simple p4config file representation and parsing.
	'''
	VALIDP4OPTIONS = [ 'P4CHARSET',
	                   'P4CLIENT',
	                   'P4DIFF',
	                   'P4EDITOR',
	                   'P4HOST',
	                   'P4LANGUAGE',
	                   'P4MERGE',
	                   'P4PASSWD',
	                   'P4PORT',
	                   'P4TICKETS',
	                   'P4USER' ]
	DELIMITER = '='
	
	def __init__( self, filepath ):
		self.filepath = filepath
		
		for v in self.VALIDP4OPTIONS:
			setattr( self, v, None )
	def read( self ):
		'''
		Read the contents of the config file.
		'''	
		try:
			with open( self.filepath , "r") as f:
				for line in f:
					# Only take lines with the proper delimiter
					if self.DELIMITER in line:
						# Strip quotes and linefeeds
						line = line.strip( os.linesep ).replace( '"','').replace( "'", "" )
						kv = line.split( self.DELIMITER )
						# Only add valid options that are non-empty
						if ( kv[0].upper() in self.VALIDP4OPTIONS ) and ( kv[1] ):
							setattr( self, kv[0].upper(), kv[1] )
		except IOError:
			print ('Could not read file {0}.'.format( self.filepath ))
				
	def write( self ):
		'''
		Write the currently assigned values in the config to disk at the currently set path.
		'''		
		try:
			with open( self.filepath , "w") as f:
				for v in self.VALIDP4OPTIONS:
					# Only write the settings that have values
					if getattr( self, v ):
						if " " in getattr( self, v ):
							# Wrap values with spaces in them with quotes
							f.write( '{0}{1}"{2}"\n'.format( v, self.DELIMITER, getattr( self, v ) ) )
						else:
							f.write( '{0}{1}{2}\n'.format( v, self.DELIMITER, getattr( self, v ) ) )
		except IOError:
			print ('Could not write to file {0}.'.format( self.filepath ))
			
	def setFilepath( self, filepath ):
		'''
		Set the filepath to read/write from.
		'''
		self.filepath = filepath
		
	@property
	def exists( self ):
		'''
		Return true if the file already exists
		'''
		return os.path.exists( self.filepath )
		
class P4Change(dict):
	def __init__( self ):
		self[ 'user' ] = ''
		self[ 'change' ] = None
		self[ 'description' ] = ''
		self[ 'files' ] = []
		self[ 'actions' ] = []
		self[ 'revisions' ] = []
	def __setattr__( self, attr, value ):
		if isinstance( value, str ):
			if value.isdigit():
				value = int( value )

		self[ attr ] = value
	def __getattr__( self, attr ):
		'''
		if the value of an attribute is the populateChanges function (in the root namespace), then
		the full changelist data is queried.  This is useful for commands like the p4 changes command
		(wrapped by the FetchChanges class method) which lists partial changelist data.  The method
		returns P4Change objects with partial data, and when more detailed data is required, a full
		query can be made.  This ensures minimal server interaction.
		'''
		value = self[ attr ]
		if value is populateChange:
			populateChange( self )
			value = self[ attr ]

		return value
	def __str__( self ):
		return str( self.change )
	def __int__( self ):
		return self[ 'change' ]
	__hash__ = __int__
	def __lt__( self, other ):
		return self.change < other.change
	def __le__( self, other ):
		return self.change <= other.change
	def __eq__( self, other ):
		return self.change == other.change
	def __ne__( self, other ):
		return self.change != other.change
	def __gt__( self, other ):
		return self.change > other.change
	def __ge__( self, other ):
		return self.change >= other.change
	def __len__( self ):
		return len( self.files )
	def __eq__( self, other ):
		if isinstance( other, int ):
			return self.change == other
		elif isinstance( other, str ):
			if other == 'default':
				return self.change == 0

		return self.change == other.change
	def __iter__( self ):
		return zip( self.files, self.revisions, self.actions )
	@classmethod
	def Create( cls, description, files=None ):

		#clean the description line
		description = '\n\t'.join( [ line.strip() for line in description.split( '\n' ) ] )
		info = p4Info()
		contents = '''Change:\tnew\n\nClient:\t%s\n\nUser:\t%s\n\nStatus:\tnew\n\nDescription:\n\t%s\n''' % (info.clientName, info.userName, description)

		workingDir = None
		if 'VGAME' in os.environ:
			workingDir = os.path.dirname( os.path.expandvars( '%VGAME%' ) )

		p4Proc = subprocess.Popen( 'p4 -s change -i', cwd=workingDir, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
		stdout, stderr = p4Proc.communicate( contents )
		p4Proc.wait()
		stdout = [ INFO_PREFIX_RE.sub( '', line ) for line in stdout.split( '\n' ) ]

		output = P4Output( stdout )
		changeNum = int( P4Output.START_DIGITS.match( output.change ).groups()[ 0 ] )

		new = cls()
		new.description = description
		new.change = changeNum

		if files is not None:
			p4run( 'reopen -c', changeNum, *files )

		return new
	@classmethod
	def FetchByNumber( cls, number ):
		lines = _p4run( 'describe', number )
		if not lines:
			return None

		change = cls()
		change.change = number

		toks = lines[ 0 ].split()
		if 'by' in toks:
			idx = toks.index( 'by' )
			change.user = toks[ idx+1 ]

		change.description = ''
		lineIter = iter( lines[ 2: ] )
		try:
			prefix = 'text:'
			PREFIX_LEN = len( prefix )

			line = lineIter.next()
			while line.startswith( prefix ):
				line = line[ PREFIX_LEN: ].lstrip()

				if line.startswith( 'Affected files ...' ):
					break

				change.description += line
				line = lineIter.next()

			lineIter.next()
			line = lineIter.next()
			while not line.startswith( prefix ):
				idx = line.rfind( '#' )
				depotFile = path.Path( line[ :idx ] )

				revAndAct = line[ idx + 1: ].split()
				rev = int( revAndAct[ 0 ] )
				act = revAndAct[ 1 ]

				change.files.append( depotFile )
				change.actions.append( act )
				change.revisions.append( rev )

				line = lineIter.next()
		except StopIteration:
			pass

		if change == 0:
			change.description = 'default'
			info = p4Info()
			fileInfo = _p4run( 'opened -u %s -C %s -c default' % (info.userName, info.clientName) )
			change.files = [ path.Path( f[ :f.find( '#' ) ] ) for f in fileInfo ]

		return change
	@classmethod
	def FetchByDescription( cls, description, createIfNotFound=False ):
		'''
		fetches a changelist based on a given description from the list of pending changelists
		'''
		cleanDesc = ''.join( [ s.strip() for s in description.lower().strip().split( '\n' ) ] )
		for change in cls.IterPending():
			thisDesc = ''.join( [ s.strip() for s in change.description.lower().strip().split( '\n' ) ] )
			if thisDesc == cleanDesc:
				return change

		if createIfNotFound:
			return cls.Create( description )
	@classmethod
	def FetchChanges( cls, *args ):
		'''
		effectively runs the command:
		p4 changes -l *args

		a list of P4Change objects is returned
		'''
		lines = _p4run( 'changes -l %s' % ' '.join( args ) )
		changes = []
		if lines:
			lineIter = iter( lines )
			curChange = None
			try:
				while True:
					line = lineIter.next()
					if line.startswith( 'Change' ):
						curChange = cls()
						changes.append( curChange )
						toks = line.split()
						curChange.change = int( toks[ 1 ] )
						curChange.user = toks[ -1 ]
						curChange.date = datetime.date( *list( map( int, toks[ 3 ].split( '/' ) ) ) )
						curChange.description = ''

						#setup triggers for other data in the changelist that doesn't get returned by the changes command - see the __getattr__ doc for more info
						curChange.files = populateChange
						curChange.actions = populateChange
						curChange.revisions = populateChange
					elif curChange is not None:
						curChange.description += line
			except StopIteration:
				return changes
	@classmethod
	def IterPending( cls ):
		'''
		iterates over pending changelists
		'''
		info = p4Info()
		changes = _p4run( 'changes -u %s -s pending -c %s' % (info.userName, info.clientName) )
		
		if changes[0].startswith( 'error:' ):
			raise P4Exception( 'Could not retreive changelist data from Perforce server!\n{0}'.format( changes[0] ) )
		
		for line in changes:
			toks = line.split()
			try:
				changeNum = int( toks[ 1 ] )
			except IndexError: continue

			yield cls.FetchByNumber( changeNum )


#the number of the default changelist
P4Change.CHANGE_NUM_DEFAULT = P4Change()
P4Change.CHANGE_NUM_DEFAULT.change = 0

#the object to represent invalid changelist numbers
P4Change.CHANGE_NUM_INVALID = P4Change()

#all opened perforce files get added to a changelist with this description by default
DEFAULT_CHANGE = 'Tools Auto-Checkout'

#gets called when a perforce command takes too long (defined by path.P4File.TIMEOUT_PERIOD)
P4_LENGTHY_CALLBACK = None

#gets called when a lengthy perforce command finally returns
P4_RETURNED_CALLBACK = None

def lsP4( queryStr, includeDeleted=False ):
	'''
	returns a list of dict's containing the clientFile, depotFile, headRev, headChange and headAction
	'''
	filesAndDicts = []
	queryLines = _p4run( 'files', queryStr )
	for line in queryLines:
		fDict = {}

		toks = line.split( ' ' )

		#deal with error lines, or exit lines (an exit prefix may not actually mean the end of the data - the query may have been broken into batches)
		if line.startswith( 'exit' ):
			continue

		if line.startswith( 'error' ):
			continue

		fData = toks[ 0 ]
		idx = fData.index( '#' )
		f = path.Path( fData[ :idx ] )
		fDict[ 'depotPath' ] = f

		rev = int( fData[ idx+1: ] )
		fDict[ 'headRev' ] = rev

		action = toks[ 2 ]
		fDict[ 'headAction' ] = action

		if action == 'delete' and not includeDeleted:
			continue

		fDict[ 'headChange' ] = toks[ 4 ]

		filesAndDicts.append( (f, fDict) )

	diskPaths = toDiskPaths( [f[0] for f in filesAndDicts] )

	lsResult = []
	for diskPath, (f, fDict) in zip( diskPaths, filesAndDicts ):
		fDict[ 'clientFile' ] = diskPath
		lsResult.append( fDict )

	return lsResult


def toDepotAndDiskPaths( files ):
	caseMatters = path.Path.DoesCaseMatter()

	lines = []
	for filesChunk in iterBy( files, 15 ):
		lines += _p4run( '-ztag where', *filesChunk )[ :-1 ]  #last line is the "exit" line...

	paths = []
	lineIter = iter( lines )
	for line in lineIter:
		if not line.startswith( 'depotFile' ):
			break

		idx = line.find( ' ' )
		depotFile = path.Path( line[ idx+1: ].strip() )

		#get the client mapped file - and throw it away
		line = lineIter.next()
		if not line.startswith( 'clientFile' ):
			break

		#now get the filepath
		line = lineIter.next()
		if not line.startswith( 'path' ):
			break

		idx = line.find( ' ' )
		filepath = path.Path( line[ idx+1: ].strip() )

		paths.append( (depotFile, filepath) )

	return paths


def toDepotPaths( files ):
	'''
	return the depot paths for the given list of disk paths
	'''
	return [ depot for depot, disk in toDepotAndDiskPaths( files ) ]


def toDiskPaths( files ):
	'''
	return the depot paths for the given list of disk paths
	'''
	return [ disk for depot, disk in toDepotAndDiskPaths( files ) ]


def isPerforceEnabled():
	return path.P4File.USE_P4


def enablePerforce( state=True ):
	'''
	sets the enabled state of perforce
	'''
	path.P4File.USE_P4 = bool( state )


def disablePerforce():
	'''
	alias for enablePerforce( False )
	'''
	enablePerforce( False )


def d_preserveDefaultChange(f):
	'''
	decorator to preserve the default changelist
	'''
	def newF( *a, **kw ):
		global DEFAULT_CHANGE
		preChange = DEFAULT_CHANGE
		try: f( *a, **kw )
		except:
			DEFAULT_CHANGE = preChange
			raise

		DEFAULT_CHANGE = preChange

	newF.__doc__ = f.__doc__
	newF.__name__ = f.__name__

	return newF


def syncFiles( files, force=False, rev=None, change=None ):
	'''
	syncs a given list of files to either the headRev (default) or a given changelist,
	or a given revision number
	'''
	p4 = path.P4File()
	if rev is not None:
		ret = []
		for f in files:
			if force:
				r = p4.sync( '-f', f, rev )
			else:
				r = p4.sync( f, rev )

			ret.append( r )

		return ret
	elif change is not None:
		args = [ 'sync' ]
		if force:
			args.append( '-f' )

		args += [ '%s@%d' % (f, change) for f in files ]

		return p4run( *args )
	else:
		args = files
		if force:
			args = [ '-f' ] + args

		return p4.run( 'sync', *args )


def findStaleFiles( fileList ):
	'''
	given a list of files (can be string paths or Path instances) returns a list of "stale" files.  stale files are simply
	files that aren't at head revision
	'''
	p4 = path.P4File()
	stale = []
	for f in fileList:
		latest = p4.isLatest( f )
		if latest is None:
			continue

		if not latest:
			stale.append( f )

	return stale


def gatherFilesIntoChange( files, change=None ):
	'''
	gathers the list of files into a single changelist - if no change is specified, then the
	default change is used
	'''
	p4 = path.P4File()
	filesGathered = []
	for f in files:
		if not isinstance( f, Path ): f = path.Path( f )

		try:
			stat = p4.getStatus( f )
		except IndexError: continue

		if not stat:
			try:
				if not f.exists:
					continue
			except TypeError: continue

			#in this case, the file isn't managed by perforce - so add it
			print ('adding file:', f)
			p4.add( f )
			p4.setChange(change, f)
			filesGathered.append( f )
			continue

		#otherwise, see what the action is on the file - if there is no action then the user hasn't
		#done anything to the file, so move on...
		try:
			action = stat[ 'action' ]
			p4.setChange( change, f )
			filesGathered.append( f )
		except KeyError: continue

	return filesGathered


def cleanEmptyChanges():
	p4 = path.P4File()
	for change in P4Change.IterPending():
		deleteIt = False
		try:
			deleteIt = not change.files
		except KeyError: deleteIt = True

		if deleteIt:
			p4run( 'change -d', str( change ) )


def findRedundantPYCs( rootDir=None, recursive=True ):
	'''
	lists all orphaned files under a given directory.  it does this by looking at the pyc/pyo file and seeing if its corresponding
	py file exists on disk, or in perforce in any form.  if it does, it deletes the file...
	'''
	if rootDir is None:
		rootDir = tools()

	bytecodeExtensions = [ 'pyc', 'pyo' ]
	exceptions = [ 'p4' ]

	rootDir = path.Path( rootDir )
	orphans = []
	if rootDir.exists:
		p4 = path.P4File()
		files = rootDir.files( recursive=recursive )
		bytecodeFiles = []
		for f in files:
			for byteXtn in bytecodeExtensions:
				if f.hasExtension( byteXtn ):
					if f.name().lower() in exceptions:
						continue

					bytecodeFiles.append( f )

		for f in bytecodeFiles:
			pyF = path.Path( f ).setExtension( 'py' )

			#is there a corresponding py script for this file?  if it does, the pyc is safe to delete - so delete it
			if pyF.exists:
				f.reason = 'corresponding py script found'
				orphans.append( f )
				continue

			#if no corresponding py file exists for the pyc, then see if there is/was one in perforce...  if the
			#corresponding py file is in perforce in any way, shape or form, then delete the .pyc file - its derivative and
			#can/will be re-generated when needed
			stat = p4.getStatus( pyF )
			if stat is None:
				continue

			f.reason = 'corresponding py file in perforce'
			orphans.append( f )

	return rootDir, orphans


def deleteRedundantPYCs( rootDir=None, recursive=True, echo=False ):
	'''
	does a delete on orphaned pyc/pyo files
	'''
	rootDir, orphans = findRedundantPYCs( rootDir, recursive )

	for f in orphans:
		if echo:
			try:
				print (f - rootDir, f.reason)
			except AttributeError:
				pass

		f.delete()

#end
