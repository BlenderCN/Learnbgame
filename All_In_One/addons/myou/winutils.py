import subprocess

def get_current_HWND():
    hwnd = subprocess.Popen(
        ['powershell','-Command',"""[CmdletBinding()]
Param(
)
Add-Type @"
  using System;
  using System.Runtime.InteropServices;
  public class UserWindows {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
}
"@
try {[UserWindows]::GetForegroundWindow()   } catch {}"""],
        stdout=subprocess.PIPE).communicate()[0].decode().replace('\r\n','')
    print('->', hwnd)
    return hwnd

def folder_dialog():
    out = subprocess.Popen(
        ['powershell','-Command',"""Function BuildDialog {
$sourcecode = @"
using System;
using System.Windows.Forms;
using System.Reflection;
namespace FolderSelect
{
	public class FolderSelectDialog
	{
		System.Windows.Forms.OpenFileDialog ofd = null;
		public FolderSelectDialog()
		{
			ofd = new System.Windows.Forms.OpenFileDialog();
			ofd.Filter = "Folders|\n";
			ofd.AddExtension = false;
			ofd.CheckFileExists = false;
			ofd.DereferenceLinks = true;
			ofd.Multiselect = false;
		}
		public string InitialDirectory
		{
			get { return ofd.InitialDirectory; }
			set { ofd.InitialDirectory = value == null || value.Length == 0 ? Environment.CurrentDirectory : value; }
		}
		public string Title
		{
			get { return ofd.Title; }
			set { ofd.Title = value == null ? "Select a folder" : value; }
		}
		public string FileName
		{
			get { return ofd.FileName; }
		}
		public bool ShowDialog()
		{
			return ShowDialog(IntPtr.Zero);
		}
		public bool ShowDialog(IntPtr hWndOwner)
		{
			bool flag = false;

			if (Environment.OSVersion.Version.Major >= 6)
			{
				var r = new Reflector("System.Windows.Forms");
				uint num = 0;
				Type typeIFileDialog = r.GetType("FileDialogNative.IFileDialog");
				object dialog = r.Call(ofd, "CreateVistaDialog");
				r.Call(ofd, "OnBeforeVistaDialog", dialog);
				uint options = (uint)r.CallAs(typeof(System.Windows.Forms.FileDialog), ofd, "GetOptions");
				options |= (uint)r.GetEnum("FileDialogNative.FOS", "FOS_PICKFOLDERS");
				r.CallAs(typeIFileDialog, dialog, "SetOptions", options);
				object pfde = r.New("FileDialog.VistaDialogEvents", ofd);
				object[] parameters = new object[] { pfde, num };
				r.CallAs2(typeIFileDialog, dialog, "Advise", parameters);
				num = (uint)parameters[1];
				try
				{
					int num2 = (int)r.CallAs(typeIFileDialog, dialog, "Show", hWndOwner);
					flag = 0 == num2;
				}
				finally
				{
					r.CallAs(typeIFileDialog, dialog, "Unadvise", num);
					GC.KeepAlive(pfde);
				}
			}
			else
			{
				var fbd = new FolderBrowserDialog();
				fbd.Description = this.Title;
				fbd.SelectedPath = this.InitialDirectory;
				fbd.ShowNewFolderButton = false;
				if (fbd.ShowDialog(new WindowWrapper(hWndOwner)) != DialogResult.OK) return false;
				ofd.FileName = fbd.SelectedPath;
				flag = true;
			}
			return flag;
		}
	}
	public class WindowWrapper : System.Windows.Forms.IWin32Window
	{
		public WindowWrapper(IntPtr handle)
		{
			_hwnd = handle;
		}
		public IntPtr Handle
		{
			get { return _hwnd; }
		}

		private IntPtr _hwnd;
	}
	public class Reflector
	{
		string m_ns;
		Assembly m_asmb;
		public Reflector(string ns)
			: this(ns, ns)
		{ }
		public Reflector(string an, string ns)
		{
			m_ns = ns;
			m_asmb = null;
			foreach (AssemblyName aN in Assembly.GetExecutingAssembly().GetReferencedAssemblies())
			{
				if (aN.FullName.StartsWith(an))
				{
					m_asmb = Assembly.Load(aN);
					break;
				}
			}
		}
		public Type GetType(string typeName)
		{
			Type type = null;
			string[] names = typeName.Split('.');

			if (names.Length > 0)
				type = m_asmb.GetType(m_ns + "." + names[0]);

			for (int i = 1; i < names.Length; ++i) {
				type = type.GetNestedType(names[i], BindingFlags.NonPublic);
			}
			return type;
		}
		public object New(string name, params object[] parameters)
		{
			Type type = GetType(name);
			ConstructorInfo[] ctorInfos = type.GetConstructors();
			foreach (ConstructorInfo ci in ctorInfos) {
				try {
					return ci.Invoke(parameters);
				} catch { }
			}

			return null;
		}
		public object Call(object obj, string func, params object[] parameters)
		{
			return Call2(obj, func, parameters);
		}
		public object Call2(object obj, string func, object[] parameters)
		{
			return CallAs2(obj.GetType(), obj, func, parameters);
		}
		public object CallAs(Type type, object obj, string func, params object[] parameters)
		{
			return CallAs2(type, obj, func, parameters);
		}
		public object CallAs2(Type type, object obj, string func, object[] parameters) {
			MethodInfo methInfo = type.GetMethod(func, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
			return methInfo.Invoke(obj, parameters);
		}
		public object Get(object obj, string prop)
		{
			return GetAs(obj.GetType(), obj, prop);
		}
		public object GetAs(Type type, object obj, string prop) {
			PropertyInfo propInfo = type.GetProperty(prop, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
			return propInfo.GetValue(obj, null);
		}
		public object GetEnum(string typeName, string name) {
			Type type = GetType(typeName);
			FieldInfo fieldInfo = type.GetField(name);
			return fieldInfo.GetValue(null);
		}
	}
}
"@
	$assemblies = ('System.Windows.Forms', 'System.Reflection')
	Add-Type -TypeDefinition $sourceCode -ReferencedAssemblies $assemblies -ErrorAction STOP
}
$fsd = New-Object FolderSelect.FolderSelectDialog
    $fsd.Title = "What to select";
    $fsd.ShowDialog() | Out-Null
$fsd.FileName"""],
        stdout=subprocess.PIPE).communicate()[0].decode().replace('\r\n','')
    print('->', out)
    return out
