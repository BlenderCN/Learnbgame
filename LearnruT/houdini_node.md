=========================Compositing nodes =====================================


Acoustic----Design audio filters and sound materials for the spatial audio system.

Agent----Imports an animation clip from an agent primitive.

Area----Calculates the area under a channel’s graph, which is the same as calculating the integral of a channel, or integrating the channel.

Attribute----Adds, removes or updates attributes of the input chop.

Audio In----Receives audio input from the analog audio ports or the digital port.

Band EQ----A 14-band equalizer which filters audio input channels in the same way that a conventional band equalizer uses a bank of sliders to filter fixed-frequency bands of sound.

Beat----Manually tap the beat of a piece of music, and automatically generate a repeating ramp or pulse that continues to keep time with the music after the taps stop.

Blend----Combines two or more chops in input 2, 3 and so on, by using a set of blending channels in input 1.

BlendPose----Performs multi-dimensional, example-based interpolation of channels.

Channel----Creates channels from the value of its parameters.

Channel VOP----Contains a VOP network that can manipulate channel data.

Channel Wrangle----Runs a VEX snippet to modify channel data.

Composite----Layers (blends) the channels of one CHOP on the channels of another CHOP.

Constant----Create up to forty new channels.

Constraint Blend----Combines two or more chops by using a list of weights specified as parameters.

Constraint Get Local Space----Returns an Object Local Transform.

Constraint Get Parent Space----Returns an Object Parent Transform.

*	[Constraint Get World Space](.)----Returns an Object World Transform.

Constraint Lookat----Constrains rotation so it always points toward a target position.

Constraint Object----Compares two objects and returns information on their relative positions and orientations.

Constraint Object Offset----Compares two objects and returns information on their relative positions and orientations.

Constraint Object Pretransform----Returns an Object Pretransform.

Constraint Offset----Applies an transformation offset after evaluating a constraint.

Constraint Parent----Reparent an object.

Constraint Path----Position an object on a path and orient it to the path’s direction.

Constraint Points----Position and Orient an object using point positions from a geometry.

Constraint Sequence----Combines multiple chops by blending the inputs in sequence.

Constraint Simple Blend----Combines two chops by using a single weight specified as a parameter.

Constraint Surface----Position and Orient an object using the surface of a geometry.

Constraint Transform----Takes translate, rotate, and/or scale channels and transforms them.

Copy----Produces multiple copies of the second input along the timeline of the first input.

Count----Counts the number of times a channel crosses a trigger or release threshold.

Cycle----Creates cycles.

Delay----Delays the input, and can be run in normal or time-sliced mode.

Delete----Removes channels coming from its input.

Device Transform----Turns data from device inputs into transform data

Dynamics----Extracts any information from a DOP simulation that is accessible through the dopfield expression function.

Envelope----Outputs the maximum amplitude in the vicinity of each sample of the input.

Euler Rotation Filter----Fixes discontinuity of rotation data after cracking matrices

Export----A convenient tool for exporting channels.

Export Constraints----Export Constraints Network on any object

Expression----Modify input channels by using expressions.

Extend----Only sets the "extend conditions" of a chop, which determines what values you get when sampling the CHOP before or after its interval.

Extract Bone Transforms----Extracts the current world or local space bone transforms from a geometry object.

Extract Locomotion----Extracts locomotion from an animation clip.

Extract Pose-Drivers----Creates channels from the specified derived transforms, node parameters and CHOP channels for pose-space deformation.

FBX----Reads in channel data from an FBX file.

Fan----Used for controlling other CHOPs.

Feedback----Get the state of a chop as it was one frame or time slice ago.

Fetch Channels----Imports channels from other CHOPs.

Fetch Parameters----Imports channels from other OPs.

File----Reads in channel and audio files for use by chops.

Filter----Smooths or sharpens the input channels.

Foot Plant----Computes when position channels are stationary.

Foreach----Divides the input channels into groups, cooking the contained network for each group.

Function----Provides more complicated math functions than found in the Math CHOP such as trigonometic functions, logarithmic functions, and exponential functions.

Gamepad----Turns input values for the gamepad or joystick device into channel outputs.

Geometry----Uses a geometry object to choose a sop from which the channels will be created.

Gesture

Handle----The "engine" which drives Inverse Kinematic solutions using the Handle object.

Hold----Sample and hold the value of the first input.

IKSolver----Solves inverse kinematics rotations for bone chains.

Identity----Returns an identity transform.

Image----Converts rows and/or columns of pixels in an image to CHOP channels.

Interpolate----Treats its multiple-inputs as keyframes and interpolates between them.

InverseKin----Generates channels for bone objects based on a bone chain and an end affector.

Invert----Returns an invert transform of the input.

Jiggle----Creates a jiggling effect in the translate channels passed in.

Keyboard----Turns key presses into channel output.

Lag----Adds lag and overshoot to channels.

Layer----Mix weighted layers of keyframed animation from multiple Channel CHOPs to a base Channel CHOP.

Limit----Provides a variety of functions to limit and quantize the input channels.

Logic----Converts channels of all its input chops into binary channels and combines them using a variety of logic operations.

Lookup----Uses a channel in the first input to index into a lookup table in the second input, and output values from the lookup table.

MIDI In----The MIDI In CHOP reads Note events, Controller events, Program Change events, and Timing events from both midi devices and files.

MIDI Out----The MIDI Out CHOP sends MIDI events to any available MIDI devices.

Math----Perform a variety of arithmetic operations on and between channels.

Merge----Takes multiple inputs and merges them into the output.

Mouse----Outputs X and Y screen values for the mouse device.

Mouse 3D----Turns input values for the Connexion space mouse into channel outputs.

Multiply----Post multiplies all the input transformations.

Network----Similar to the Pipe In/Out CHOPs in Network mode.

Noise----Makes an irregular wave that never repeats, with values approximately in the range -1 to +1.

Null----Used as a place-holder and does not have a function of its own.

Object----Compares two objects and returns information on their relative positions and orientations.

ObjectChain----Creates channels representing the transforms for a chain of objects.

Oscillator----Generates sounds in two ways.

Output----Marks the output of a sub-network.

Parametric EQ----Filters an audio clip, and then applies other audio effects.

Particle----Produces translate and rotate channels to move Objects according to the positions of particles in a POP Network.

Pass Filter----Filters audio input using one of four different filter types.

Phoneme----Translates english text into a series of phonetic values.

Pipe In----Pipes data from custom devices into a CHOP, without needing the Houdini Developers' Kit or knowledge of Houdini internals.

Pipe Out----Transmit data out of Houdini to other processes.

Pitch----Attempts to extract the fundamental pitch of a musical tone from the input audio.

Pose----Store a transform pose for later use by evaluating the input.

Pose Difference----Computes the difference between two poses.

Pretransform----Takes translate, rotate, and/or scale channels and transforms them using the pretransform of the given object.

Pulse----Generates pulses at regular intervals of one channel.

ROP Channel Output

Record

Rename----Renames channels.

Reorder----Reorders the first input CHOP’s channels by numeric or alphabetic patterns.

Resample----Resamples an input’s channels to a new rate and/or start/end interval.

Sequence----Takes all its inputs and appends one chop after another.

Shift----This time-shifts a CHOP, changing the start and end of the CHOP’s interval.

Shuffle----Reorganizes a list of channels.

Slope----Calculates the slope (or derivative) of the input channels.

Spatial Audio----The rendering engine for producing 3D audio.

Spectrum----Calculates the frequency spectrum of the input channels, or a portion of the channels.

Spline----Edit the channel data by using direct manipulation of cubic or Bezier handles in the graph of the CHOP.

Spring----Creates vibrations influenced by the input channels, as if a mass was attached to a spring.

Stash----Caches the input motion in the node on command, and then uses it as the node’s output.

Stash Pose----Stashes the bone transforms and pose-drivers for use by the Pose-Space Deform SOP and Pose-Space Edit SOP nodes.

Stretch----Preserves the shape of channels and the sampling rate, but resamples the channels into a new interval.

Subnetwork----Allows for the simplification of complex networks by collapsing several CHOPs into one.

Switch----Control the flow of channels through a CHOPnet.

Time Range----This converts an input node in Current Frame mode to a Time Range mode by re-cooking it multiple times.

Time Shift----This time-shifts a CHOP, re-cooking the node using different time.

Transform----Takes translate, rotate, and/or scale channels and transforms them.

TransformChain----Combines a chain of translate, rotate, and/or scale channels.

Trigger----Adds an audio-style attack/decay/sustain/release (ADSR) envelope to all trigger points in the input channels.

Trim----Shortens or lengthens the input’s channels.

VEX Waveform----This function is a sub-set of the waveform CHOP.

Vector----Performs vector operations on a set or sets of channels.

Voice Split----The Voice Split CHOP takes an audio track and separates "words" out into different channels.

Voice Sync----The Voice Sync CHOP detects phonemes in an audio channel given some audio phoneme samples and pro…

Warp----Time-warps the channels of the first input (the Pre-Warp Channels) using one warping channel in the second input.

Wave----Creates a waveform that is repeated

Add----Adds two images together.

Anaglyph----Creates an anaglyph from a pair of input images.

Atop----Composites the first input (Foreground) over the second (background), but only where the background alpha exists.

Average----Averages the foreground image and the background image.

Blend----Blends frames from two sequences together using a simple linear blend.

Blur----Blurs an image.

Border----Adds a border to the image.

Bright----Applies a brightness factor and bright shift to the first input.

Bump----Builds a bump map from a plane.

Channel Copy----Copy channels from any of inputs into the output image.

Chromakey----Mask or "key" an image based on its color.

Color----Creates a constant color image.

Color Correct----Applies a variety of color corrections to the image

Color Curve----Adjusts the R,G,B and/or A channels based on a user-defined curve.

Color Map----Maps a range of color to a new range.

Color Replace----Replace a color region in an image with another region.

Color Wheel----Generates a simple HSV color wheel.

Composite----Does a composite (over, under, inside, add, etc) between two images.

Contrast----Increases or decreases the contrast of an image.

Convert----Changes the data format of a plane.

Convolve----Performs a generic convolve on the source image.

Corner Pin----Fits an image into an arbitrary quadrilateral.

Corner Ramp----Generates a four corner ramp.

Crop----Crops an image and changes its resolution.

Cryptomatte----Extracts matte from Cryptomatte image.

DSM Flatten----Flattens a Deep Shadow/Camera Map into a flat 2D raster.

Defocus----Defocuses an image similar to a real camera defocus.

Deform----Deforms an image by moving the underlying UV coordinates.

Degrain----Removes film grain from an image.

Deinterlace----De-interlaces a frame of video by either averaging scanlines or copying a scanline.

Delete----Removes planes or components from an input sequence.

Denoise----Removes white noise from an image.

Depth Darken----Darkens depth boundaries in an image.

Depth of Field----Creates a depth-of-field mask, which describes how out of focus parts of the image are.

Diff---Computes the difference between the foreground image and the background image.

Dilate/Erode----Expands and shrinks mattes.

Drop Shadow----Creates a blurred shadow offset of an image.

Edge Blur----Blurs the edges of an image.

Edge Detect----Detects edges in the input image.

Emboss----Adds a lighting effect to the image by using a bump map.

Environment----Applies an environment map to an image.

Equalize----Equalizes colors by stretching or shifting the image histogram.

Error Function Table Generator----Creates an image containing precomputed error function terms for hair albedo computation

Expand----Expands and shrinks mattes.

Extend----Extends the length of a sequence so that it can be animated beyond its frame range.

Fetch----Fetches a sequence of images from another COP, even in another network.

Field Merge----Merges two fields into one Interlaced Frame.

Field Split----Splits an interlaced frame into two fields per frame (odd and even fields).

Field Swap----Swaps the two fields containing the even and odd scanlines of the frame.

File----Loads image files into Houdini.

Flip----Flips the image horizontally and/or vertically.

Fog----Adds a variety of atmospheric effects to an image, including fog, haze and heat waves.

Font----Renders anti-aliased text.

Front Face----Cleans up flipped normals by making them face the camera.

Function----Performs a variety of mathematical functions on the input image.

Gamma----Applies gamma correction to the image.

Geokey----Keys out parts of the image based on pixel position or normal direction.

Geometry----Renders geometry from a SOP as a single color image.

Gradient----Computes the gradient of an image.

Grain----Adds grain to an image.

HSV----Converts between RGB and HSV color spaces, or applies hue and saturation modifications.

Hue Curve----Adjusts the saturation or luminance of the image based on hue.

Illegal Pixel----Detects illegal pixels, like NAN and INF, in images.

Inside----Restricts the foreground color to the area of the background’s alpha matte.

Interleave----Interleaves image sequences.

Invert----Applies a photographic pixel inversion to the image.

Layer----Layers a series of inputs together by compositing them one by one on the background image (input 1).

Levels----Adjusts black point, white point, and midrange to increase, balance, or decrease contrast.

Lighting----Adds a light to the image.

Limit----Limits the pixel range at the high end, low end or both.

Lookup----Applies a lookup table to the input.

Loop----Cooks the subnet COPs multiple times in a loop, accumulating the results.

Luma Matte----Sets the alpha to the luminance of the color.

Lumakey----Keys the image based on luminance (or similar function).

Mask----Masks out an area of an image.

Max----Outputs the maximum value of the foreground and background images for each pixel, which tends to lighten the image.

Median----Applies a 3 x 3 or 5 x 5 median filter to the input image.

Merge----Merges the planes of several inputs together.

Metadata----Applies metadata to an image sequence.

Min----Outputs the minimum value of the foreground and background images for each pixel, which tends to darken the image.

Mono----Converts a color or vector into a scalar quantity, like luminance or length.

Mosaic----Takes a sequence of images and combines them into 1 image by tiling them.

Multiply----Multiplies the foreground image with the background image.

Noise----Generates continuous noise patterns.

Null----Does nothing.

Outside----Restricts the foreground color to the area outside of the background’s alpha matte.

Over----Composites the first input (Foreground) over the second (background).

Pixel----Modifies an image’s pixels using expressions.

Premultiply----Allows colour to be converted to or from a premultiplied form.

Pulldown----Performs a pulldown (cine-expand) on the input sequence.

Pushup----Performs a pushup (cine-expand) on the input sequence.

Quantize----Quantizes input data into discrete steps.

ROP File Output----Renders frames out to disk.

Radial Blur----Does a radial or angular blur.

Ramp----Generates a variety of linear and radial ramps, which are fully keyframable.

Reference----Copies the sequence information from its input.

Rename----Change the name a plane.

Render----Renders a mantra output driver directly into a composite network.

Reverse----Simply reverses the frames in the sequence.

Rotoshape----Draws one or more curves or shapes.

SOP Import----Imports a 2d Volume from SOPs as planes into a composite network.

Scale----Changes the resolution of the image.

Screen----Adds two images together, saturating at white like photographic addition.

Sequence----Sequences two or more inputs end to end.

Shape----Generates simple shapes, such as circles, stars and regular N-sided polygons.

Sharpen----Sharpens an image by enhancing the contrast of edges.

Shift----Shifts an image sequence in time.

Shuffle----Shuffle frames around to do out-of-order editing.

Sky Environment Map----Creates sky and ground images for use as environment maps.

Snip----Either removes frames from a sequence or allows you to order them in a user-defined order.

Streak Blur----Streaks an image, adding a motion blur effect.

Subnetwork----Contains networks of other COPs.

Subtract----Subtracts the foreground image from the background image.

Switch----Passes the input of one of its connected inputs through, acting like an exclusive switch.

Switch Alpha----Replaces input 1's alpha with input 2's alpha.

Terrain Noise----Generate noise suitable for terrain height maps.

Tile----Tiles the image sequence with multiple copies of the input image.

Time Filter----Blurs a pixel through several frames.

Time Machine----Uses a second input to time warp the first input on a per pixel basis.

Time Scale----Stretches or compresses a sequence in time.

Time Warp----Warps time by slowing or speeding it up throughout the sequence.

Transform----Translates, rotates and/or scales the input image without changing the image resolution.

Trim----Trims an input sequence in time by adjusting the beginning or the end of the sequence.

UV Map----Creates a UV map.

Under----Composites the first input (Foreground) under the second (background).

Unpin----Extracts an arbitrary quadrilateral area out of the input image.

VEX Filter----Runs a VEX script on its input planes.

VEX Generator----Runs a VEX script on the planes it generates.

VOP COP2 Filter----Contains a VOP network that filters input image data.

VOP COP2 Generator----Contains a VOP network that generates image data.

Vector----Performs vector operations on the input.

Velocity Blur----Blurs an image by using pixel velocity to produce a motion blur effect.

Window----Cuts a small window out of a larger image.

Wipe----Does a wipe between two input sequences.

Xor----Makes two elements mutually exclusive; if their alpha mattes overlap, the overlap is removed.

Z Comp----Does a Z composite of two images.



================================================================================




===========================Dynamics nodes ==================================
Active Value----Marks a simulation object as active or passive.

Affector----Creates affector relationships between groups of objects.

Agent Arcing Clip Layer----Blends between a set of animation clips based on the agent’s turn rate.

Agent Clip Layer----Layers additional animation clips onto an agent.

Agent Look At----Chooses an object/position for the head of an agent to look at.

Agent Look At Apply----Moves the head of an agent to look at a target.

Agent Terrain Adaptation----Adapts the legs of an agent to conform to terrain and prevent the feet from sliding.

Agent Terrain Adaptation----Adapts the legs of a biped agent to conform to terrain.

Agent Terrain Projection----Project the agent/particle points onto the terrain

Anchor: Align Axis----Defines an orientation that aligns an axis in object space with a second axis defined by the relative locations of two positional anchors.

Anchor: Object Point Group Position----Defines multiple points, specified by their number or group, on the given geometry of a simulation object.

Anchor: Object Point Group Rotation----Defines orientations based on multiple points on the given geometry of a simulation object.

Anchor: Object Point Id Position----Defines a position by looking at the position of a point on the geometry of a simulation object.

Anchor: Object Point Id Rotation----Defines an orientation by looking at a point on the geometry of a simulation object.

Anchor: Object Point Number Position----Defines a position by looking at the position of a point on the geometry of a simulation object.

Anchor: Object Point Number Rotation----Defines an orientation by looking at a point on the geometry of a simulation object.

Anchor: Object Primitive Position----Defines a position by looking at the position of a particular UV coordinate location on a primitive.

Anchor: Object Space Position----Defines a position by specifying a position in the space of some simulation object.

Anchor: Object Space Rotation----Defines an orientation by specifying a rotation in the space of some simulation object.

Anchor: Object Surface Position----Defines multiple attachment points on a polygonal surface of an object.

Anchor: World Space Position----Defines a position by specifying a position in world space.

Anchor: World Space Rotation----Defines an orientation by specifying a rotation in world space.

Apply Data----Attaches data to simulation objects or other data.

Apply Relationship----Creates relationships between simulation objects.

Blend Factor

Blend Solver

Bullet Data----Attaches the appropriate data for Bullet Objects to an object.

Bullet Soft Constraint Relationship

Bullet Solver----Sets and configures an Bullet Dynamics solver.

Buoyancy Force----Applies a uniform force to objects submerged in a fluid.

Cloth Attach Constraint----Constrains a set of points on a cloth object to the surface of a Static Object.

Cloth Configure Object----Attaches the appropriate data for Cloth Objects to an object.

Cloth Mass Properties----Defines the mass properties.

Cloth Material----Defines the physical material for a deformable surface.

Cloth Material Behavior----Defines the internal cloth forces.

Cloth Object----Creates a Cloth Object from SOP Geometry.

Cloth Object----Creates a Cloth Object from SOP Geometry.

Cloth Plasticity Properties----Defines the plasticity properties.

Cloth Stitch Constraint----Constrains part of the boundary of a cloth object to the boundary of another cloth object.

Cloth Target Properties----Defines how cloth uses target.

Cloth Visualization

Cloth/Volume Collider----Defines a way of resolving collisions involving a cloth object and DOPs objects with volumetric representations (RBD Objects, ground planes, etc.)

Collide Relationship

Collider Label

Cone Twist Constraint----Constrains an object to remain a certain distance from the constraint, and limits the object’s rotation.

Cone Twist Constraint Relationship

Constraint

Constraint Network----Constrains pairs of RBD objects together according to a polygon network.

Constraint Network Relationship-----Defines a set of constraints based on geometry.

Constraint Network Visualization----Visualizes the constraints defined by constraint network geometry.

Constraint Relationship

Container

Copy Data----Creates multiple copies of the input data.

Copy Data Solver----Sets and configures a Copy Data Solver.

Copy Object Information----Mimics the information set by the Copy Object DOP.

Copy Objects

Crowd Fuzzy Logic----Defines a Crowd Fuzzy Logic

Crowd Object----Creates a crowd object with required agent attributes to be used in the crowd simulation.

Crowd Solver----Updates agents according to their steer forces and animation clips.

Crowd Solver----Update crowd agents based on the custom steerforces and adjusting animation playback of clips

Crowd State----Defines a Crowd State

Crowd State----Defines a Crowd State.

Crowd Transition----Defines a transition between crowd states.

Crowd Transition----Defines a transition between crowd states.

Crowd Trigger----Defines a Crowd Trigger

Crowd Trigger----Defines a Crowd Trigger

Crowd Trigger Logic----Combines multiple crowd triggers to build a more complex trigger.

Data Only Once----Adds a data only once to an object, regardless of number of wires.

Delete----Deletes both objects and data according to patterns.

Drag Force----Applies force and torque to objects that resists their current direction of motion.

Drag Properties----Defines how the surrounding medium affects a soft body object.

Embedding Properties----Controls Embedded Geometry that can be deformed along with the simulated geometry in a finite element simulation.

Empty Data----Creates an Empty Data for holding custom information.

Empty Object----Creates an Empty Object.

Empty Relationship

Enable Solver

FEM Fuse Constraint----Constrains points of a solid object or a hybrid object to points of another DOP object.

FEM Hybrid Object----Creates an FEM Hybrid Object from SOP Geometry.

FEM Region Constraint----Constrains regions of a solid object or a hybrid object to another solid or hybrid object.

FEM Solid Object----Creates a simulated FEM solid from geometry.

FEM Solver----Sets and configures a Finite Element solver.

FEM Target Constraint----Constrains an FEM object to a target trajectory using a hard constraint or soft constraint.

FLIP Configure Object----Attaches the appropriate data for Particle Fluid Objects to become a FLIP based fluid.

FLIP Solver----Evolves an object as a FLIP fluid object.

FLIP fluid object

Fan Force----Applies forces on the objects as if a cone-shaped fan were acting on them.

Fetch Data----Fetches a piece of data from a simulation object.

Field Force----Applies forces to an object using some piece of geometry as a vector field.

Filament Object----Creates a vortex filament object from SOP Geometry.

Filament Solver----Evolves vortex filament geometry over time.

Filament Source----Imports vortex filaments from a SOP network.

File----Saves and loads simulation objects to external files.

File Data

Finite Element Output Attributes----Allows a finite-element object to generate optional output attributes.

Fluid Configure Object----Attaches the appropriate data for Fluid Objects to an object.

Fluid Force----Applies forces to resist the current motion of soft body objects relative to a fluid.

Fluid Object----Attaches the appropriate data for Fluid Objects to an object.

Fluid Solver----A solver for Sign Distance Field (SDF) liquid simulations.

Gas Adjust Coordinate System----A microsolver that adjusts an internal coordinate system attached to fluid particles in a particle fluid simulation.

Gas Advect----A microsolver that advects fields and geometry by a velocity field.

Gas Advect CL----A microsolver that advects fields and geometry by a velocity field using OpenCL acceleration.

Gas Advect Field----A microsolver that advects fields and geometry by a velocity field.

Gas Analysis----A microsolver that computes analytic property of fields.

Gas Attribute Swap----A microsolver that swaps geometry attributes.

Gas Blend Density----A microsolver that blends the density of two fields.

Gas Blur----A microsolver that blurs fields.

Gas Build Collision Mask----A microsolver that determines the collision field between the fluid field and any affector objects.

Gas Build Relationship Mask----A microsolver that builds a mask for each voxel to show the presence or absence of relationships between objects.

Gas Buoyancy----A microsolver that calculates an adhoc buoyancy force and updates a velocity field.

Gas Calculate----A microsolver that performs general calculations on a pair of fields.

Gas Collision Detect----A microsolver that detects collisions between particles and geometry.

Gas Combustion----A microsolver that applies a combustion model to the simulation.

Gas Correct By Markers----A microsolver that adjusts an SDF according to surface markers.

Gas Cross----A microsolver that computes the cross product of two vector fields.

Gas Curve Force----A DOP node that creates forces generated from a curve.

Gas Damp----A microsolver that scales down velocity, damping motion.

Gas Diffuse----A microsolver that diffuses a field or point attribute.

Gas Dissipate----A microsolver that dissipates a field.

Gas Disturbance----Adds detail at a certain scale by applying "disturbance" forces to a scalar or vector field.

Gas Each Data Solver----A microsolver that runs once for each matching data.

Gas Embed Fluid----A microsolver that embeds one fluid inside another.

Gas Enforce Boundary----A microsolver that enforces boundary conditions on a field.

Gas Equalize Density----A microsolver that equalizes the density of two fields.

Gas Equalize Volume----A microsolver that equalizes the volume of two fields.

Gas External Forces----A microsolver that evaluates the external DOPs forces for each point in a velocity field and updates the velocity field accordingly.

Gas Extrapolate----A microsolver that extrapolates a field’s value along an SDF.

Gas Feather Field----A microsolver that creates a feathered mask out of a field.

Gas Feedback----A microsolver that calculates and applies feedback forces to collision geometry.

Gas Fetch Fields to Embed----A data node that fetches the fields needed to embed one fluid in another.

Gas Field VOP----Runs CVEX on a set of fields.

Gas Field Wrangle----Runs CVEX on a set of fields.

Gas Field to Particle----A microsolver that copies the values of a field into a point attribute on geometry.

Gas Geometry Defragment----A microsolver that defragments geometry.

Gas Geometry to SDF----A microsolver that creates a signed distance field out of geometry.

Gas Guiding Volume----Blends a set of SOP volumes into a set of new collision fields for the creation of a guided simulation.

Gas Impact to Attributes----A microsolver that copies Impact data onto point attributes.

Gas Integrator----A microsolver that applies forces to a particle fluid system.

Gas Intermittent Solve----A microsolver that solves its subsolvers at a regular interval.

Gas Limit----A microsolver that clamps a field within certain values.

Gas Limit Particles----A microsolver that keeps particles within a box.

Gas Linear Combination----A microsolver that combines multiple fields or attributes together.

Gas Local Sharpen----A microsolver that adaptively sharpens a field.

Gas Lookup----A microsolver that looksup field values according to a position field.

Gas Match Field----A microsolver that rebuilds fields to match in size and resolution to a reference field.

Gas Net Fetch Data----A microsolver that arbitrary simulation data between multiple machines.

Gas Net Field Border Exchange----A microsolver that exchanges boundary data between multiple machines.

Gas Net Field Slice Exchange----A microsolver that exchanges boundary data between multiple machines.

Gas Net Slice Balance----A microsolver that balances slices data between multiple machines.

Gas Net Slice Exchange----A microsolver that exchanges boundary data between multiple machines.

Gas OpenCL----Executes the provided kernel with the given parameters.

Gas Particle Count----A microsolver that counts the number of particles in each voxel of a field.

Gas Particle Forces----A microsolver that computes pairwise collision forces between particles that represent instanced spheres.

Gas Particle Move to Iso----A microsolver that moves particles to lie along a certain isosurface of an SDF.

Gas Particle Separate----A microsolver that separates adjacent particles by adjusting their point positions..

Gas Particle to Field----A microsolver that copies a particle system’s point attribute into a field.

Gas Particle to SDF----A microsolver that converts a particle system into a signed distance field.

Gas Project Non Divergent----A microsolver that removes the divergent components of a velocity field.

Gas Project Non Divergent Multigrid----A microsolver that removes the divergent components of a velocity field using a multi-grid method.

Gas Project Non Divergent Variational----A microsolver that removes the divergent components of a velocity field.

Gas Reduce----A microsolver that reduces a field to a single constant field .

Gas Reduce Local----A microsolver that reduces surrounding voxels to a single value.

Gas Reinitialize SDF----A microsolver that reinitializes a signed distance field while preserving the zero isocontour.

Gas Repeat Solver----A microsolver that repeatedly solves its input.

Gas Resize Field----A microsolver that changes the size of fields.

Gas Resize Fluid Dynamic----A microsolver that resizes a fluid to match simulating fluid bounds

Gas Rest----A microsolver that initializes a rest field.

Gas SDF to Fog----A microsolver that converts an SDF field to a Fog field.

Gas Sand Forces----A microsolver that computes the forces to treat the fluid simulation as sand rather than fluid.

Gas Seed Markers----A microsolver that seeds marker particles around the boundary of a surface.

Gas Seed Particles----A microsolver that seeds particles uniformly inside a surface.

Gas Shred----Applies a Shredding Force to the velocity field specified.

Gas Slice To Index Field----A microsolver that computes slice numbers into an index field.

Gas Stick on Collision----Adjusts a fluid velocity field to match collision velocities.

Gas Strain Forces----A microsolver that calculates the forces imparted by a strain field.

Gas Strain Integrate----A microsolver that updates the strain field according to the current velocity field.

Gas SubStep----A microsolver that substeps input microsolvers.

Gas Surface Snap----A microsolver that snaps a surface onto a collision surface.

Gas Surface Tension----A microsolver that calculates a surface tension force proportional to the curvature of the surface field.

Gas Target Force----A microsolver that applies a force towards a target object.

Gas Temperature Update----Modifies the temperature of a FLIP over time.

Gas Turbulence----Applies Turbulence to the specified velocity field.

Gas Up Res----Up-scales and/or modifies a smoke, fire, or liquid simulations.

Gas Velocity Stretch----A microsolver that reorients geometry according to motion of a velocity field.

Gas Viscosity----A microsolver that applies viscosity to a velocity field.

Gas Volume----A microsolver that seeds flip particles into a new volume region.

Gas Volume Ramp----Remaps a field according to a ramp.

Gas Vortex Boost----Applies a confinement force on specific bands of sampled energy.

Gas Vortex Confinement----Applies a vortex confinement force to a velocity field.

Gas Vortex Equalizer----Applies a confinement force on specific bands of sampled energy.

Gas Vorticle Forces----A microsolver that applies forces to a velocity field or geometry according to vorticle geometry.

Gas Vorticle Geometry----A DOP node that adds the appropriately formatted data to represent vorticles.

Gas Vorticle Recycle----A DOP node that recycles vorticles by moving them to the opposite side of the fluid box when they leave.

Gas Wavelets----A microsolver that performs a wavelet decomposition of a field.

Gas Wind----A microsolver that applies a wind force.

Geometry Copy

Geometry VOP----Runs CVEX on geometry attributes.

Geometry Wrangle----Runs a VEX snippet to modify attribute values.

Glue Constraint Relationship

Gravity Force----Applies a gravity-like force to objects.

Ground Plane----Creates a ground plane suitable for RBD or cloth simulations.

Group----Creates simulation object groups.

Group Relationship

Hard Constraint Relationship----Defines a constraint relationship that must always be satisfied.

Hybrid Configure Object----Attaches the appropriate data for Hybrid Objects to an object.

Impact Analysis----Stores filtered information about impacts on an RBD object.

Impulse Force----Applies an impulse to an object.

Index Field----Creates an index field.

Index Field Visualization----Visualizes an index field.

Instanced Object----Creates DOP Objects according to instance attributes

Intangible Value----Marks a simulation object as intangible or tangible.

Link to Source Object----Stores the name of the scene level object source for this DOP object.

Magnet Force----Apply forces on objects using a force field defined by metaballs.

Mask Field

Matrix Field----Creates a matrix field.

Matrix Field Visualization----Visualizes a matrix field.

Merge----Merges multiple streams of objects or data into a single stream.

Modify Data----Modifies or creates options on arbitrary data.

Motion----Defines an object’s position, orientation, linear velocity, and angular velocity.

Multi Field Visualization----Unified visualization of multiple fields.

Multiple Solver

Net Fetch Data----A DOP that transfers arbitrary simulation data between multiple machines.

No Collider

No Constraint Relationship

Noise Field

Null----Does nothing.

OBJ Position----Creates position information from an object’s transform.

Output----Serves as the end-point of the simulation network. Has controls for writing out sim files.

POP Advect by Filaments----Uses vortex filaments to move particles.

POP Advect by Volumes----A POP node that uses velocity volumes to move particles.

POP Attract----A POP node that attracts particles to positions and geometry.

POP Attribute from Volume----A POP node that copies volume values into a particle attribute.

POP Awaken----A POP node that resets the stopped attribute on particles, waking them up.

POP Axis Force----A POP node that applies a force around an axis.

POP Collision Behavior----A POP node that reacts to collisions.

POP Collision Detect----A POP node that detects and reacts to collisions.

POP Collision Ignore----A POP node marks particles to ignore implicit collisions.

POP Color----A POP node that colors particles.

POP Curve Force----A POP node that creates forces generated from a curve.

POP Drag----A POP node that applies drag to particles.

POP Drag Spin----A POP node that applies drag to the spin of particles.

POP Fan Cone----A POP node that applies a conical fan wind to particles.

POP Fireworks----A POP node that creates a simple fireworks system.

POP Float by Volumes----A POP node that floats particles on the surface of a liquid simulation.

POP Flock----A POP node that applies a flocking algorithm to particles.

POP Fluid----Controls local density by applying forces between nearby particles.

POP Force----A POP node that applies forces to particles.

POP Grains----A POP node that applies sand grain interaction to particles.

POP Group----A POP node that groups particles.

POP Instance----A POP node that sets up the instancepath for particles.

POP Interact----A POP node that applies forces between particles.

POP Kill----A POP node that kills particles.

POP Limit----A POP node that limits particles.

POP Local Force----A POP node that applies forces within the particle’s frame.

POP Location----A POP solver that generates particles at a point.

POP Lookat----A POP node makes a particle look at a point.

POP Metball Force----A POP node that applies forces according to metaballs.

POP Object----Converts a regular particle system into a dynamic object capable of interacting correctly with other objects in the DOP environment.

POP Property----A POP node that sets various common attributes on particles.

POP Proximity----A POP node that sets attributes based on nearby particles.

POP Replicate----A POP Node that generates particles from incoming particles.

POP Soft Limit----A POP node that creates a spongy boundary.

POP Solver----A POP solver updates particles according to their velocities and forces.

POP Source----A POP node that generates particles from geometry.

POP Speed Limit----A POP node that sets the speed limits for particles.

POP Spin----A POP node that sets the spin of particles..

POP Spin by Volumes----A POP node that uses the vorticity of velocity volumes to spin particles.

POP Sprite----A POP node that sets the sprite display for particles.

POP Steer Align----Applies force to agents/particles to align them with neighbors.

POP Steer Avoid----Applies anticipatory avoidance force to agents/particles to avoid potential future collisions with other agents/particles.

POP Steer Cohesion----Applies forces to agents/particles to bring them closer to their neighbors.

POP Steer Custom----Applies forces to agents/particles calulated using a VOP network.

POP Steer Obstacle----Applies force to agents/particles to avoid potential collisions with static objects.

POP Steer Obstacle----Applies force to agents/particles to avoid potential collisions with static objects.

POP Steer Path----Applies force to agents/particles according to directions from a path curve.

POP Steer Seek----Applies force to agents/particles to move them toward a target position.

POP Steer Separate----Apply force to agents/particles to move them apart from each other.

POP Steer Solver----Used internally in the crowd solver to integrate steering forces.

POP Steer Solver----Used internally in the crowd solver to integrate custom steering forces.

POP Steer Turn Constraint----Constrains agent velocity to only go in a direction within a certain angle range of its current heading, to prevent agents from floating backward.

POP Steer Wander----Apply forces to agents/particles to create a random motion.

POP Stream----A POP node that creates a new stream of particles.

POP Torque----A POP node that applies torque to particles, causing them to spin.

POP VOP----Runs CVEX on a particle system.

POP Velocity----A POP node that directly changes the velocity of particles.

POP Wind----A POP node that applies wind to particles.

POP Wrangle----Runs a VEX snippet to modify particles.

Particle Fluid Emitter----Emits particles into a particle fluid simulation.

Particle Fluid Sink----Removes fluid particles that flow inside of a specified boundary from a simulation.

Particle Fluid Visualization----Visualizes particles.

Partition----Creates simulation object groups based on an expression.

Physical Parameters----Defines the base physical parameters of DOP objects.

Point Collider

Point Force----Applies a force to an object from a particular location in space.

Point Position----Creates position information from a point on some SOP geometry.

Position----Associates a position and orientation to an object.

Pump Relationship

Pyro Solver----Sets and configures a Pyro solver. This solver can be used to create both fire and smoke.

RBD Angular Constraint----Constrains an RBD object to a certain orientation.

RBD Angular Spring Constraint----Constrains an RBD object to have a certain orientation, but with a set amount of springiness.

RBD Auto Freeze----Automatically freezes RBD Objects that have come to rest

RBD Configure Object----Attaches the appropriate data for RBD Objects to an object.

RBD Fractured Object----Creates a number of RBD Objects from SOP Geometry. These individual RBD Objects are created from the geometry name attributes.

RBD Hinge Constraint----Constrains an object to two constraints, creating a rotation similar to a hinge or a trapeze bar.

RBD Keyframe Active

RBD Object----Creates an RBD Object from SOP Geometry.

RBD Packed Object----Creates a single DOP object from SOP Geometry that represents a number of RBD Objects.

RBD Pin Constraint----Constrains an RBD object a certain distance from the constraint.

RBD Point Object----Creates a simulation object at each point of some source geometry, similarly to how the Copy surface node copies geometry onto points.

RBD Solver----Sets and configures a Rigid Body Dynamics solver.

RBD Spring Constraint----Constrains an object to remain a certain distance from the constraint, with a set amount of springiness.

RBD State----Alters the state information for an RBD Object.

RBD Visualization

ROP Output Driver----Saves the state of a DOP network simulation into files.

Reference Frame Force----Applies forces to an object according to the difference between two reference frames.

Rendering Parameters Volatile

Rigid Body Solver----Sets and configures a Rigid Body Dynamics solver.

Ripple Configure Object----Attaches the appropriate data for Ripple Objects to an object.

Ripple Object----Creates an object from existing geometry that will be deformed with the ripple solver.

Ripple Solver----Animates wave propagation across Ripple Objects.

SDF Representation----Creates a signed distance field representation of a piece of geometry that can be used for collision detection.

SOP Geometry

SOP Guide

SOP Merge Field----A microsolver that performs general calculations on a pair consisting of a DOP field and a SOP volume/VDB.

SOP Scalar Field----Creates a scalar field from a SOP Volume.

SOP Solver

SOP Vector Field----Creates a vector field from a SOP Volume Primitive.

Scalar Field----Creates a scalar field.

Scalar Field Visualization----Visualizes a scalar field.

Script Solver

Seam Properties----Defines the internal seam angle.

Shell Mass Properties----Defines the mass density of a Cloth Object.

Sink Relationship

Slice Along Line----Divides a particle system uniformly into multiple slices along a line.

Slice by Plane----Specifies a cutting plane to divide a particle system into two slices for distributed simulations.

Slider Constraint----Constrains an object to rotate and translate on a single axis, and limits the rotation and translation on that axis.

Slider Constraint Relationship

Smoke Configure Object----Attaches the appropriate data for Smoke Objects to an object.

Smoke Object----Creates an Smoke Object from SOP Geometry.

Smoke Solver----Sets and configures a Smoke solver. This is a slightly lower-level solver that is the basis for the Pyro solver.

Soft Attach Constraint Relationship

Soft Body (SBD) Constraint----Constrains a set of points on a soft body object to a certain position using a hard constraint or soft constraint.

Soft Body (SBD) Pin Constraint----Constrains a point on a soft body object to a certain position.

Soft Body (SBD) Spring Constraint----Constrains a point on a soft body to a certain position, with a set amount of springiness.

Soft Body Collision Properties----Defines how a soft body object responds to collisions.

Soft Body Fracture Properties----Defines how a Soft Body Object responds to collisions.

Soft Body Fracture Properties----Defines how a Soft Body Object responds to collisions.

Soft Body Material Properties----Defines how a Soft Body Object responds to collisions.

Soft Body Rest Properties----Allows the user to import the rest state from a SOP node.

Soft Body Solver----Sets and configures a Soft Body solver.

Soft Body Target Properties----Defines the strengths of the soft constraint on a soft body object.

Solid Aniso Multiplier----Controls the anisotropic behavior of a Solid Object.

Solid Configure Object----Attaches the appropriate data for Solid Objects to an object.

Solid Mass Properties----Defines the mass density of a Solid Object.

Solid Model Data----Defines how a Solid Object reacts to strain and change of volume.

Solid Object----Creates a Solid Object from SOP Geometry.

Solid Solver

Solid Visualization

Source Relationship

Sphere Edge Tree----This builds a tree of spheres producing bounding information for an edge cloud.

Sphere Point Tree----This builds a tree of spheres producing bounding information for a point cloud.

Split Object----Splits an incoming object stream into as many as four output streams.

Spring Constraint Relationship

Static Object----Creates a Static Object from SOP Geometry.

Static Solver

Static Visualization----Allows you to inspect the behavior of a static object in the viewport.

Subnetwork

Surface Collision Parameters----Control the thickness of the object that collides with cloth.

Switch----Passes one of the input object or data streams to the output.

Switch Solver

Switch Value

Target Relationship

Terrain Object----Creates a Terrain Object from SOP Geometry.

Thin Plate/Thin Plate Collider----Defines a way of resolving collisions between two rigid bodies.

Two State Constraint Relationship

Uniform Force----Applies a uniform force and torque to objects.

VOP Force----Applies forces on the objects according to a VOP network.

Vector Field----Creates a vector field.

Vector Field Visualization

Visualizes a vector field.

Vellum Constraint Property----Modifies common Vellum Constraint properties during a Vellum solve.

Vellum Constraints----Microsolver to create Vellum constraints during a simulation.

Vellum Object----Creates a DOP Object for use with the Vellum Solver.

Vellum Rest Blend----Blends the current rest values of constraints with a rest state calculated from the current simulation or external geometry.

Vellum Solver----Sets and configures a Vellum solver.

Vellum Source----A Vellum node that creates Vellum patches.

Velocity Impulse Force----Applies an impulse to an object.

Visualize Geometry----A microsolver to create soft references to visualizers on itself.

Volume Source----Imports SOP source geometry into smoke, pyro, and FLIP simulations.

Volume/Volume Collider----Defines a way of resolving collisions involving two rigid bodies with volume.

Voronoi Fracture Configure Object----Attaches the appropriate data to make an object fractureable by the Voronoi Fracture Solver

Voronoi Fracture Parameters----Defines the parameters for dynamic fracturing using the Voronoi Fracture Solver

Voronoi Fracture Solver----Dynamically fractures objects based on data from the Voronoi Fracture Configure Object DOP

Vortex Force----Applies a vortex-like force on objects, causing them to orbit about an axis along a circular path.

Whitewater Object----Creates a Whitewater Object that holds data for a whitewater simulation.

Whitewater Object----Creates a Whitewater Object that holds data for a whitewater simulation.

Whitewater Solver----Sets and configures a Whitewater Solver.

Whitewater Solver----Sets and configures a Whitewater solver.

Wind Force----Applies forces to resist the current motion of objects relative to a turbulent wind.

Wire Angular Constraint----Constrains a wire point’s orientation to a certain direction.

Wire Angular Spring Constraint----Constrains a wire point’s orientation to a certain direction, with a set amount of springiness.

Wire Configure Object----Attaches the appropriate data for Wire Objects to an object.

Wire Elasticity----Defines the elasticity of a wire object.

Wire Glue Constraint----Constraints a wire point to a certain position and direction.

Wire Object----Creates a Wire Object from SOP Geometry.

Wire Physical Parameters----Defines the physical parameters of a wire object.

Wire Plasticity----Defines the plasticity of a wire object.

Wire Solver----Sets and configures a Wire solver.

Wire Visualization

Wire/Volume Collider----Defines a way of resolving collisions involving a wire object and DOPs objects with volumetric representations.

Wire/Wire Collider----Defines a way of resolving collisions between two wires.

clothsolver

clothsolver-

finiteelementsolver




====================================================================================



==============================Object nodes ==================================


Agent Cam----Create and attach camera to a crowd agent.

Alembic Archive----Loads the objects from an Alembic scene archive (.abc) file into the object level.

Alembic Xform----Loads only the transform from an object or objects in an Alembic scene archive (.abc).

Ambient Light----Adds a constant level of light to every surface in the scene (or in the light’s mask), coming from no specific direction.

Auto Bone Chain Interface----The Auto Bone Chain Interface is created by the IK from Objects and IK from Bones tools on the Rigging shelf.

Blend----Switches or blends between the transformations of several input objects.

Blend Sticky----Computes its transform by blending between the transforms of two or more sticky objects, allowing you to blend a position across a polygonal surface.

Bone----The Bone Object is used to create hierarchies of limb-like objects that form part of a hierarchy …

COP2 Plane----Container for the Compositing operators (COP2) that define a picture.

Camera----You can view your scene through a camera, and render from its point of view.

Dop Network----The DOP Network Object contains a dynamic simulation.

Environment Light----Environment Lights provide background illumination from outside the scene.

Extract Transform----The Extract Transform Object gets its transform by comparing the points of two pieces of geometry.

Fetch----The Fetch Object gets its transform by copying the transform of another object.

Formation Crowd Example----Crowd example showing a changing formation setup

Franken Muscle----Creates a custom muscle by combining any number of geometry objects, muscle rigs, and muscle pins.

Fuzzy Logic Obstacle Avoidance Example

Fuzzy Logic State Transition Example

Geometry----Container for the geometry operators (SOPs) that define a modeled object.

Groom Merge----Merges groom data from multiple objects into one.

Guide Deform----Moves the curves of a groom with animated skin.

Guide Groom----Generates guide curves from a skin geometry and does further processing on these using an editable SOP network contained within the node.

Guide Simulate---Runs a physics simulation on the input guides.

Hair Card Generate----Converts dense hair curves to a polygon card, keeping the style and shape of the groom.

Hair Card Texture Example----An example of how to create a texture for hair cards.

Hair Generate----Generates hair from a skin geometry and guide curves.

Handle----The Handle Object is an IK tool for manipulating bones.

Indirect Light----Indirect lights produce illumination that has reflected from other objects in the scene.

Instance----Instance Objects can instance other geometry, light, or even subnetworks of objects.

Light----Light Objects cast light on other objects in a scene.

Light template----A very limited light object without any built-in render properties. Use this only if you want to build completely custom light with your choice of properties.

Microphone----The Microphone object specifies a listening point for the SpatialAudio CHOP.

Mocap Acclaim----Import Acclaim motion capture.

Mocap Biped 1----A male character with motion captured animations.

Mocap Biped 2----A male character with motion captured animations.

Mocap Biped 3----A male character with motion captured animations.

Muscle----The Muscle object is a versatile tool that can be used when rigging characters and creatures with musculature.

Muscle Pin----Creates a simple rigging component for attaching regions of a Franken Muscle to your character rig.

Muscle Rig----Creates the internal components of a muscle (the rig), by stroking a curve onto a skin object.

Null----Serves as a place-holder in the scene, usually for parenting. this object does not render.

Path----The Path object creates an oriented curve (path)

PathCV----The PathCV object creates control vertices used by the Path object.

Pxr AOV Light----Pxr AOV Light object for RenderMan RIS.

Pxr Barn Light Filter----Pxr Barn Light Filter object for RenderMan RIS.

Pxr Blocker Light Filter----Pxr Blocker Light Filter object for RenderMan RIS.

Pxr Cookie Light Filter----Pxr Cookie Light Filter object for RenderMan RIS.

Pxr Day Light----Pxr Day Light object for RenderMan RIS.

Pxr Disk Light----Pxr Disk Light object for RenderMan RIS.

Pxr Distant Light----Pxr Distant Light object for RenderMan RIS.

Pxr Dome Light----Pxr Dome Light object for RenderMan RIS.

Pxr Gobo Light Filter----Pxr Gobo Light Filter object for RenderMan RIS.

Pxr Mesh Light----Pxr Mesh Light object for RenderMan RIS.

Pxr Portal Light----Pxr Portal Light object for RenderMan RIS.

Pxr Ramp Light Filter----Pxr Ramp Light Filter object for RenderMan RIS.

Pxr Rectangle Light----Pxr Rectangle Light object for RenderMan RIS.

Pxr Rod Light Filter----Pxr Rod Light Filter object for RenderMan RIS.

Pxr Sphere Light----Pxr Sphere Light object for RenderMan RIS.

Python Script----The Python Script object is a container for the geometry operators (SOPs) that define a modeled object.

Ragdoll Run Example----Crowd example showing a simple ragdoll setup.

Rivet----Creates a rivet on an objects surface, usually for parenting.

Simple Biped----A simple and efficient animation rig with full controls.

Simple Female----A simple and efficient female character animation rig with full controls.

Simple Male----A simple and efficient male character animation rig with full controls.

Sound----The Sound object defines a sound emission point for the Spatial Audio chop.

Stadium Crowds Example----Crowd example showing a stadium setup

Stereo Camera Rig----Provides parameters to manipulate the interaxial lens distance as well as the zero parallax setting plane in the scene.

Stereo Camera Template----Serves as a basis for constructing a more functional stereo camera rig as a digital asset.

Sticky----Creates a sticky object based on the UV’s of a surface, usually for parenting.

Street Crowd Example----Crowd example showing a street setup with two agent groups

Subnet----Container for objects.

Switcher----Acts as a camera but switches between the views from other cameras.

Tissue Solver----Collects muscles, anatomical bone models, and skin objects and places them into a single dynamics simulation.

Toon Character----A ready-to-animate Toon Character.

Top Network----The TOP Network Object contains nodes to running tasks

VR Camera----Camera supporting VR image rendering.

Viewport Isolator----A Python Script HDA providing per viewport isolation controls from selection.

glTF

pxr Int Mult Light Filter----pxr Int Mult Light Filter object for RenderMan RIS.





================================================================================



==============================Render nodes =======================================


Agent----This output operator is used to write agent definition files.

Alembic

Archive Generator----Generates disk-based archives which can be used by either mantra or RIB renderers.

Bake Animation----Bakes animation from object transforms and CHOP overrides.

Bake Texture----Generates a texture map from one or more objects' rendered appearance.

Batch----Renders the input ROP in a single batch job.

Brick Map Generator----Allows you to convert Houdini volume primitives into Pixar brickmap files.

Channel----The Channel output operator generates clip files from a particular CHOP.

Composite----The Composite output operator renders the image(s) produced in the Compositing Editor.

DSM Merge----Merges two or more deep shadow/camera map files.

Dynamics----Saves the state of a DOP network simulation into files.

Fetch----Makes a dependency link to a ROP in a different network.

Filmbox FBX----Exports entire scenes to FBX files.

Frame Container----Prevents frame dependency changes in the contained nodes from affecting its inputs.

Frame Depedency----Allows an output frame to depend on one or more input frames.

Geometry----Generates geometry files from a SOP or DOP network.

HQueue Render----HQueue, or Houdini Queue, is a distributed job scheduling system.

HQueue Simulation----HQueue, or Houdini Queue, is a distributed job scheduling system.

Hair Card Texture----Renders hair textures for use on hair cards.

MDD Point Cache----This output operator is used to write an MDD animation file.

Mantra----Renders the scene using Houdini’s standard mantra renderer and generates IFD files.

Mantra Archive----Generates disk-based archives which can be used by mantra.

Merge----Merges several render dependencies into one.

Net Barrier----Blocks the ROP network until synchronization occurs.

Null----Does nothing.

OpenGL----Render an image using the hardware-accelerated 3D viewport renderer.

Pre Post----Renders ROPs before and after a main job.

RenderMan----Renders the scene using Pixar’s RenderMan renderer.

RenderMan----Renders the scene using Pixar’s RenderMan RIS renderer.

RenderMan Archive----Generates disk-based archives which can be used by RenderMan .

Shell----Runs an external command.

Subnetwork----The SubNetwork output operator provides an easy way to manage large number of output operators.

Switch----Renders one of several inputs.

Tractor----Tractor is a program shipped out with Pixar’s distribution of RenderMan.

Wedge----Re-renders the same ROP multiple times with different settings

Wren----This output operator is used to drive the Wren rendering program.

glTF

glTF




==================================================================================



========================================= Geometry nodes=============================



Adaptive Prune----Removes elements while trying to maintain the overall appearance.

Add----Creates Points or Polygons, or adds points/polys to an input.

Agent----Creates agent primitives.

Agent Clip----Adds new clips to agent primitives.

Agent Clip----Adds new clips to agent primitives.

Agent Clip Properties----Defines how agents' animation clips should be played back.

Agent Clip Transition Graph----Creates geometry describing possible transitions between animation clips.

Agent Collision Layer----Creates a new agent layer that is suitable for collision detection.

Agent Configure Joints----Creates point attributes that specify the rotation limits of an agent’s joints.

Agent Constraint Network----Builds a constraint network to hold an agent’s limbs together.

Agent Definition Cache----Writes agent definition files to disk.

Agent Edit----Edits properties of agent primitives.

Agent Layer----Adds a new layer to agent primitives.

Agent Look At----Adjusts the head of an agent to look at a specific object or position.

Agent Look At----Adjusts the head of an agent to look at a specific object or position.

Agent Prep----Adds various common point attributes to agents for use by other crowd nodes.

Agent Prep----Adds various common point attributes to agents for use by other crowd nodes.

Agent Proxy----Provides simple proxy geometry for an agent.

Agent Relationship----Creates parent-child relationships between agents.

Agent Terrain Adaptation----Adapts agents' legs to conform to terrain and prevent the feet from sliding.

Agent Transform Group----Adds new transform groups to agent primitives.

Agent Unpack----Extracts geometry from agent primitives.

Agent Vellum Unpack----Extracts geometry from agent primitives for a Vellum simulation.

Alembic----Loads the geometry from an Alembic scene archive (.abc) file into a geometry network.

Alembic Group----Creates a geometry group for Alembic primitives.

Alembic Primitive----Modifies intrinsic properties of Alembic primitives.

Alembic ROP output driver

Align----Aligns a group of primitives to each other or to an auxiliary input.

Assemble----Cleans up a series of break operations and creates the resulting pieces.

Attribute Blur----Blurs out (or "relaxes") points in a mesh or a point cloud.

*	[Attribute Cast](.)----Changes the size/precision Houdini uses to store an attribute.

Attribute Composite----Composites vertex, point, primitive, and/or detail attributes between two or more selections.

Attribute Copy----Copies attributes between groups of vertices, points, or primitives.

Attribute Create----Adds or edits user defined attributes.

Attribute Delete----Deletes point and primitive attributes.

Attribute Expression----Allows simple VEX expressions to modify attributes.

Attribute Fade----Fades a point attribute in and out over time.

Attribute Interpolate----Interpolates attributes within primitives or based on explicit weights.

Attribute Mirror----Copies and flips attributes from one side of a plane to another.

Attribute Noise----Adds noise to attributes of the incoming geometry.

Attribute Promote----Promotes or demotes attributes from one geometry level to another.

Attribute Randomize----Generates random attribute values of various distributions.

Attribute Rename----Renames or deletes point and primitive attributes.

Attribute Reorient----Modifies point attributes based on differences between two models.

Attribute String Edit----Edits string attribute values.

Attribute Swap----Copies, moves, or swaps the contents of attributes.

Attribute Transfer----Transfers vertex, point, primitive, and/or detail attributes between two models.

Attribute Transfer By UV----Transfers attributes between two geometries based on UV proximity.

Attribute VOP----Runs a VOP network to modify geometry attributes.

Attribute Wrangle----Runs a VEX snippet to modify attribute values.

Attribute from Map----Samples texture map information to a point attribute.

Attribute from Volume----Copies information from a volume onto the point attributes of another piece of geometry, with optional remapping.

Bake ODE----Converts primitives for ODE and Bullet solvers.

Bake Volume----Computes lighting values within volume primitives

Basis----Provides operations for moving knots within the parametric space of a NURBS curve or surface.

Bend----Applies deformations such as bend, taper, squash/stretch, and twist.

Blast----Deletes primitives, points, edges or breakpoints.

Blend Shapes----Computes a 3D metamorphosis between shapes with the same topology.

Blend Shapes----Computes a 3D metamorphosis between shapes with the same topology.

Block Begin----The start of a looping block.

Block Begin Compile----The start of a compile block.

Block End----The end/output of a looping block.

Block End Compile----The end/output of a compile block.

Bone Capture----Supports Bone Deform by assigning capture weights to bones.

Bone Capture Biharmonic----Supports Deform by assigning capture weights to points based on biharmonic functions on tetrahedral meshes.

Bone Capture Lines----Supports Bone Capture Biharmonic by creating lines from bones with suitable attributes.

Bone Capture Proximity----Supports Bone Deform by assigning capture weights to points based on distance to bones.

Bone Deform----Uses capture attributes created from bones to deform geometry according to their movement.

Bone Link----Creates default geometry for Bone objects.

Boolean----Combines two polygonal objects with boolean operators, or finds the intersection lines between two polygonal objects.

Boolean Fracture----Fractures the input geometry using cutting surfaces.

Bound----Creates a bounding box, sphere, or rectangle for the input geometry.

Box----Creates a cube or six-sided rectangular box.

Bulge----Deforms the points in the first input using one or more magnets from the second input.

Cache----Records and caches its input geometry for faster playback.

Cap----Closes open areas with flat or rounded coverings.

Capture Attribute Pack----Converts array attributes into a single index-pair capture attribute.

Capture Attribute Unpack----Converts a single index-pair capture attribute into per-point and detail array attributes.

Capture Correct----Adjusts capture regions and capture weights.

Capture Layer Paint----Lets you paint capture attributes directly onto geometry.

Capture Mirror----Copies capture attributes from one half of a symmetric model to the other.

Capture Override----Overrides the capture weights on individual points.

Capture Region----Supports Capture and Deform operation by creating a volume within which points are captured to a bone.

Carve----Slices, cuts or extracts points or cross-sections from a primitive.

Channel----Reads sample data from a chop and converts it into point positions and point attributes.

Circle----Creates open or closed arcs, circles and ellipses.

Clay----Lets you deform NURBS faces and NURBS surfaces by pulling points that lie directly on them.

Clean----Helps clean up dirty models.

Clip----Removes or groups geometry on one side of a plane, or creases geometry along a plane.

Cloth Capture----Captures low-res simulated cloth.

Cloth Deform----Deforms geometry captured by the Cloth Capture SOP.

Cloud----Creates a volume representation of source geometry.

Cloud Light----Fills a volume with a diffuse light.

Cloud Noise----Applies a cloud like noise to a Fog volume.

Cluster----Low-level machinery to cluster points based on their positions (or any vector attribute).

Cluster Points----Higher-level node to cluster points based on their positions (or any vector attribute).

Collision Source----Creates geometry and VDB volumes for use with DOPs collisions.

Color----Adds color attributes to geometry.

Comb----Adjust surface point normals by painting.

Connect Adjacent Pieces----Creates lines between nearby pieces.

Connectivity----Creates an attribute with a unique value for each set of connected primitives or points.

Control----Creates simple geometry for use as control shapes.

Convert----Converts geometry from one geometry type to another.

Convert HeightField----Converts a 2D height field to a 3D VDB volume, polygon surface, or polygon soup surface.

Convert Line----Converts the input geometry into line segments.

Convert Meta----Polygonizes metaball geometry.

Convert Tets----Generates the oriented surface of a tetrahedron mesh.

Convert VDB----Converts sparse volumes.

Convert VDB Points----Converts a Point Cloud into a VDB Points Primitive, or vice versa.

Convert Volume----Converts the iso-surface of a volume into a polygonal surface.

Convex Decomposition----Decomposes the input geometry into approximate convex segments.

Copy Stamp----Creates multiple copies of the input geometry, or copies the geometry onto the points of the second input.

Copy and Transform----Copies geometry and applies transformations to the copies.

Copy to Points----Copies the geometry in the first input onto the points of the second input.

Crease----Manually adds or removes a creaseweight attribute to/from polygon edges, for use with the Subdivide SOP.

Creep----Deforms and animates a piece of geometry across a surface.

Crowd Source----Populates a crowd of agent primitives.

Crowd Source----Creates crowd agents to be used with the crowd solver.

Curve----Creates polygonal, NURBS, or Bezier curves.

Curveclay----Deforms a spline surface by reshaping a curve on the surface.

Curvesect----Finds the intersections (or points of minimum distance) between two or more curves or faces.

DOP I/O----Imports fields from DOP simulations, saves them to disk, and loads them back again.

DOP Import Fields----Imports scalar and vector fields from a DOP simulation.

DOP Import Records----Imports option and record data from DOP simulations into points with point attributes.

DOP Network

Debris Source----Generates point emission sources for debris from separating fractured rigid body objects.

Deformation Wrangle----Runs a VEX snippet to deform geometry.

Delete----Deletes input geometry by group, entity number, bounding volume, primitive/point/edge normals, and/or degeneracy.

DeltaMush----Smooths out (or "relaxes") point deformations.

Detangle----Attempts to prevent collisions when deforming geometry.

Dissolve----Deletes edges from the input polygonal geometry merging polygons with shared edges.

Dissolve----Deletes points, primitives, and edges from the input geometry and repairs any holes left behind.

Divide----Divides, smooths, and triangulates polygons.

Dop Import----Imports and transforms geometry based on information extracted from a DOP simulation.

Draw Curve----Creates a curve based on user input in the viewport.

Draw Guides

Each----Culls the input geometry according to the specifications of the For Each SOP.

Edge Collapse----Collapses edges and faces to their centerpoints.

Edge Cusp----Sharpens edges by uniquing their points and recomputing point normals.

Edge Divide----Inserts points on the edges of polygons and optionally connects them.

Edge Flip----Flips the direction of polygon edges.

Edge Fracture----Cuts geometry along edges using guiding curves.

Edge Transport----Copies and optionally modifies attribute values along edges networks and curves.

Edit----Edits points, edges, or faces interactively.

Ends----Closes, opens, or clamps end points.

Enumerate----Sets an attribute on selected points or primitives to sequential numbers.

Error----Generates a message, warning, or error, which can show up on a parent asset.

Exploded View----Pushes geometry out from the center to create an exploded view.

Exploded View----Pushes geometry out from the center to create an exploded view.

Extract Centroid----Computes the centroid of each piece of the geometry.

Extract Transform----Computes the best-fit transform between two pieces of geometry.

Extrude----Extrudes geometry along a normal.

Extrude Volume----Extrudes surface geometry into a volume.

FEM Visualization

FLIP Source----Creates a surface or density VDB for sourcing FLIP simulations.

Facet----Controls the smoothness of faceting of a surface.

Falloff----Adds smooth distance attributes to geometry.

Filament Advect----Evolves polygonal curves as vortex filaments.

File----Reads, writes, or caches geometry on disk.

File Cache----Writes and reads geometry sequences to disk.

File Merge----Reads and collates data from disk.

Fillet----Creates smooth bridging geometry between two curves or surfaces.

Filmbox FBX ROP output driver

Find Shortest Path----Finds the shortest paths from start points to end points, following the edges of a surface.

Fit----Fits a spline curve to points, or a spline surface to a mesh of points.

Fluid Compress----Compresses the output of fluid simulations to decrease size on disk

Font----Creates 3D text from Type 1, TrueType and OpenType fonts.

Force----Uses a metaball to attract or repel points or springs.

Fractal----Creates jagged mountain-like divisions of the input geometry.

Fur---Creates a set of hair-like curves across a surface.

Fuse----Merges points.

Fuse----Merges or splits (uniques) points.

Glue Cluster----Adds strength to a glue constraint network according to cluster values.

Grain Source----Generates particles to be used as sources in a particle-based grain simulation.

Graph Color----Assigns a unique integer attribute to non-touching components.

Grid----Creates planar geometry.

Groom Blend----Blends the guides and skin of two grooms.

Groom Fetch----Fetches groom data from grooming objects.

Groom Pack----Packs the components of a groom into a set of named Packed Primitives for the purpose of writing it to disk.

Groom Switch----Switches between all components of two groom streams.

Groom Unpack----Unpacks the components of a groom from a packed groom.

Group----Generates groups of points, primitives, edges, or vertices according to various criteria.

Group Combine----Combines point groups, primitive groups, or edge groups according to boolean operations.

Group Copy----Copies groups between two pieces of geometry, based on point/primitive numbers.

Group Delete----Deletes groups of points, primitives, edges, or vertices according to patterns.

Group Expression----Runs VEX expressions to modify group membership.

Group Paint----Sets group membership interactively by painting.

Group Promote----Converts point, primitive, edge, or vertex groups into point, primitive, edge, or vertex groups.

Group Range----Groups points and primitives by ranges.

Group Rename----Renames groups according to patterns.

Group Transfer----Transfers groups between two pieces of geometry, based on proximity.

Guide Advect----Advects guide points through a velocity volume.

Guide Collide With VDB----Resolves collisions of guide curves with VDB signed distance fields.

Guide Deform----Deforms geometry with an animated skin and optionally guide curves.

Guide Groom----Allows intuitive manipulation of guide curves in the viewport.

Guide Group----Creates standard primitive groups used by grooming tools.

Guide Initialize----Quickly give hair guides some initial direction.

Guide Mask----Creates masking attributes for other grooming operations.

Guide Partition----Creates and prepares parting lines for use with hair generation.

Guide Skin Attribute Lookup----Looks up skin geometry attributes under the root point of guide curves.

Guide Tangent Space----Constructs a coherent tangent space along a curve.

Guide Transfer----Transfer hair guides between geometries.

Hair Card Generate----Converts dense hair curves to a polygon card, keeping the style and shape of the groom.

Hair Clump----Clumps guide curves together.

Hair Generate----Generates hair on a surface or from points.

Hair Growth Field----Generates a velocity field based on stroke primitives.

HeightField----Generates an initial heightfield volume for use with terrain tools.

HeightField Blur----Blurs a terrain height field or mask.

HeightField Clip----Limits height values to a certain minimum and/or maximum.

HeightField Copy Layer----Creates a copy of a height field or mask.

HeightField Crop----Extracts a square of a certain width/length from a larger height volume, or resizes/moves the boundaries of the height field.

HeightField Cutout by Object----Creates a cutout on a terrain based on geometry.

HeightField Distort by Layer----Displaces a height field by another field.

HeightField Distort by Noise----Advects the input volume through a noise pattern to break up hard edges and add variety.

HeightField Draw Mask----Lets you draw shapes to create a mask for height field tools.

HeightField Erode----Calculates thermal and hydraulic erosion over time (frames) to create more realistic terrain.

HeightField Erode----Calculates thermal and hydraulic erosion over time (frames) to create more realistic terrain.

HeightField Erode Hydro----Simulates the erosion from one heightfield sliding over another for a short time.

HeightField Erode Precipitation----Distributes water along a heightfield. Offers controls for adjusting the intensity, variability, and location of rainfall.

HeightField Erode Thermal----Calculates the effect of thermal erosion on terrain for a short time.

HeightField File----Imports a 2D image map from a file or compositing node into a height field or mask.

HeightField Flow Field----Generates flow and flow direction layers according to the input height layer.

HeightField Isolate Layer----Copies another layer over the mask layer, and optionally flattens the height field.

HeightField Layer----Composites together two height fields.

HeightField Layer Clear----Sets all values in a heightfield layer to a fixed value.

HeightField Layer Property----Sets the border voxel policy on a height field volume.

HeightField Mask by Feature----Creates a mask based on different features of the height layer.

HeightField Mask by Object----Creates a mask based some other geometry.

HeightField Mask by Occlusion----Creates a mask where the input terrain is hollow/depressed, for example riverbeds and valleys.

HeightField Noise----Adds vertical noise to a height field, creating peaks and valleys.

HeightField Output----Exports height and/or mask layers to disk as an image.

HeightField Paint----Lets you paint values into a height or mask field using strokes.

HeightField Patch----Patches features from one heightfield to another.

HeightField Pattern----Adds displacement in the form of a ramps, steps, stripes, Voronoi cells, or other patterns.

HeightField Project----Projects 3D geometry into a height field.

HeightField Quick Shade----Applies a material that lets you plug in textures for different layers.

HeightField Remap----Remaps the values in a height field or mask layer.

HeightField Resample----Changes the resolution of a height field.

HeightField Scatter----Scatters points across the surface of a height field.

HeightField Scatter----Scatters points across the surface of a height field.

HeightField Slump----Simulates loose material sliding down inclines and piling at the bottom.

HeightField Terrace----Creates stepped plains from slopes in the terrain.

HeightField Tile Splice----Stitches height field tiles back together.

HeightField Tile Split----Splits a height field volume into rows and columns.

HeightField Transform----Height field specific scales and offsets.

HeightField Visualize----Visualizes elevations using a custom ramp material, and mask layers using tint colors.

Hole----Makes holes in surfaces.

Inflate----Deforms the points in the first input to make room for the inflation tool.

Instance----Instances Geometry on Points.

Intersection Analysis----Creates points with attributes at intersections between a triangle and/or curve mesh with itself, or with an optional second set of triangles and/or curves.

Intersection Stitch----Composes triangle surfaces and curves together into a single connected mesh.

Invoke Compiled Block----Processes its inputs using the operation of a referenced compiled block.

IsoOffset----Builds an offset surface from geometry.

IsoSurface----Generates an isometric surface from an implicit function.

Join----The Join op connects a sequence of faces or surfaces into a single primitive that inherits their attributes.

Knife----Divides, deletes, or groups geometry based on an interactively drawn line.

L-System----Creates fractal geometry from the recursive application of simple rules.

Lattice----Deforms geometry based on how you reshape control geometry.

Lidar Import----Reads a lidar file and imports a point cloud from its data.

Line----Creates polygon or NURBS lines from a position, direction, and distance.

MDD----Animates points using an MDD file.

Magnet----Deforms geometry by using another piece of geometry to attract or repel points.

Match Axis----Aligns the input geometry to a specific axis.

Match Size----Resizes and recenters the geometry according to reference geometry.

Match Topology----Reorders the primitive and point numbers of the input geometry to match some reference geometry.

Material----Assigns one or more materials to geometry.

Measure----Measures area, volume, or curvature of individual elements or larger pieces of a geometry and puts the results in attributes.

Measure----Measures volume, area, and perimeter of polygons and puts the results in attributes.

Merge----Merges geometry from its inputs.

MetaGroups----Defines groupings of metaballs so that separate groupings are treated as separate surfaces when merged.

Metaball----Creates metaballs and meta-superquadric surfaces.

Mirror----Duplicates and mirrors geometry across a mirror plane.

Mountain----Displaces points along their normals based on fractal noise.

Mountain----Displaces points along their normals based on fractal noise.

Muscle Capture----Supports Muscle Deform by assigning capture weights to points based on distance away from given primitives

Muscle Deform----Deforms a surface mesh representing skin to envelop or drape over geometry representing muscles

Name----Creates a "naming" attribute on points or primitives allowing you to refer to them easily, similar to groups.

Normal----Computes surface normal attribute.

Null----Does nothing.

Object Merge----Merges geometry from multiple sources and allows you to define the manner in which they are grouped together and transformed.

Object_musclerig@musclerigstrokebuilder

Object_riggedmuscle@musclestrokebuilder----Assists the creation of a Muscle or Muscle Rig by allowing you to draw a stroke on a projection surface.

Ocean Evaluate----Deforms input geometry based on ocean "spectrum" volumes.

Ocean Evaluate----Deforms input geometry based on ocean "spectrum" volumes.

Ocean Foam----Generates particle-based foam

Ocean Source----Generates particles and volumes from ocean "spectrum" volumes for use in simulations

Ocean Source----Generates particles and volumes from ocean "spectrum" volumes for use in simulations

Ocean Spectrum----Generates volumes containing information for simulating ocean waves.

Ocean Waves----Instances individual waveforms onto input points and generated points.

OpenCL----Executes an OpenCL kernel on geometry.

Output----Marks the output of a sub-network.

Pack----Packs geometry into an embedded primitive.

Pack Points----Packs points into a tiled grid of packed primitives.

Packed Disk Edit----Editing Packed Disk Primitives.

Packed Edit----Editing Packed Primitives.

Paint----Lets you paint color or other attributes on geometry.

Paint Color Volume----Creates a color volume based on drawn curve

Paint Fog Volume----Creates a fog volume based on drawn curve

Paint SDF Volume----Creates an SDF volume based on drawn curve

Particle Fluid Surface----Generates a surface around the particles from a particle fluid simulation.

Particle Fluid Tank----Creates a set of regular points filling a tank.

Partition----Places points and primitives into groups based on a user-supplied rule.

Peak----Moves primitives, points, edges or breakpoints along their normals.

Planar Patch----Creates a planar polygonal patch.

Planar Patch from Curves----Fills in a 2d curve network with triangles.

Planar Pleat----Deforms flat geometry into a pleat.

Platonic Solids----Creates platonic solids of different types.

Point----Manually adds or edits point attributes.

Point Cloud Iso----Constructs an iso surface from its input points.

Point Deform----Deforms geometry on an arbitrary connected point mesh.

Point Generate----Creates new points, optionally based on point positions in the input geometry.

Point Jitter----Jitters points in random directions.

Point Relax----Moves points with overlapping radii away from each other, optionally on a surface.

Point Replicate----Generates a cloud of points around the input points.

Point Velocity----Computes and manipulates velocities for points of a geometry.

Points from Volume----Creates set of regular points filling a volume.

Poly Bridge----Creates flat or tube-shaped polygon surfaces between source and destination edge loops, with controls for the shape of the bridge.

Poly Expand 2D----Creates offset polygonal geometry for planar polygonal graphs.

Poly Extrude----Extrudes polygonal faces and edges.

PolyBevel----Creates straight, rounded, or custom fillets along edges and corners.

PolyBevel----Bevels points and edges.

PolyCut----Breaks curves where an attribute crosses a threshold.

PolyDoctor----Helps repair invalid polygonal geometry, such as for cloth simulation.

PolyExtrude----Extrudes polygonal faces and edges.

PolyFill----Fills holes with polygonal patches.

PolyFrame----Creates coordinate frame attributes for points and vertices.

PolyLoft----Creates new polygons using existing points.

PolyPatch----Creates a smooth polygonal patch from primitives.

PolyPath----Cleans up topology of polygon curves.

PolyReduce----Reduces the number of polygons in a model while retaining its shape. This node preserves features, attributes, textures, and quads during reduction.

PolySoup----Combines polygons into a single primitive that can be more efficient for many polygons

PolySpline----The PolySpline SOP fits a spline curve to a polygon or hull and outputs a polygonal approximation of that spline.

PolySplit----Divides an existing polygon into multiple new polygons.

PolySplit----Divides an existing polygon into multiple new polygons.

PolyStitch----Stitches polygonal surfaces together, attempting to remove cracks.

PolyWire----Constructs polygonal tubes around polylines, creating renderable geometry with smooth bends and intersections.

Pose-Space Deform----Interpolates between a set of pose-shapes based on the value of a set of drivers.

Pose-Space Deform Combine----Combine result of Pose-Space Deform with rest geometry.

Pose-Space Edit----Packs geometry edits for pose-space deformation.

Pose-Space Edit Configure----Creates common attributes used by the Pose-Space Edit SOP.

Primitive----Edits primitive, primitive attributes, and profile curves.

Primitive Split----Takes a primitive attribute and splits any points whose primitives differ by more than a specified tolerance at that attribute.

Profile----Extracts or manipulates profile curves.

Project----Creates profile curves on surfaces.

Pyro Source----Creates points for sourcing pyro and smoke simulations.

Python----Runs a Python snippet to modify the incoming geometry.

RBD Cluster----Combines fractured pieces or constraints into larger clusters.

RBD Constraint Properties----Creates attributes describing rigid body constraints.

RBD Constraints From Curves----Creates rigid body constraint geometry from curves drawn in the viewport.

RBD Constraints From Lines----Creates rigid body constraint geometry from interactively drawn lines in the viewport.

RBD Constraints From Rules----Creates rigid body constraint geometry from a set of rules and conditions.

RBD Interior Detail----Creates additional detail on the interior surfaces of fractured geometry.

RBD Material Fracture----Fractures the input geometry based on a material type.

RBD Material Fracture----Fractures the input geometry based on a material type.

RBD Pack----Packs RBD geometry, constraints, and proxy geometry into a single geometry.

RBD Paint----Paints values onto geometry or constraints using strokes.

RBD Unpack----Unpacks an RBD setup into three outputs.

RMan Shader----Attaches RenderMan shaders to groups of faces.

ROP Geometry Output

Rails----Generates surfaces by stretching cross-sections between two guide rails.

Ray----Projects one surface onto another.

Refine----Increases the number of points/CVs in a curve or surface without changing its shape.

Reguide----Scatters new guides, interpolating the properties of existing guides.

Remesh----Recreates the shape of the input surface using "high-quality" (nearly equilateral) triangles.

Repack----Repacks geometry as an embedded primitive.

Resample----Resamples one or more curves or surfaces into even length segments.

Rest Position----Sets the alignment of solid textures to the geometry so the texture stays put on the surface as it deforms.

Retime----Retimes the time-dependent input geometry.

Reverse----Reverses or cycles the vertex order of faces.

Revolve----Revolves a curve around a center axis to sweep out a surface.

Rewire Vertices----Rewires vertices to different points specified by an attribute.

Ripple----Generates ripples by displacing points along the up direction specified.

Scatter----Scatters new points randomly across a surface or through a volume.

Script----Runs scripts when cooked.

Sculpt----Lets you interactively reshape a surface by brushing.

Sequence Blend----Morphs though a sequence of 3D shapes, interpolating geometry and attributes.

Sequence Blend----Sequence Blend lets you do 3D Metamorphosis between shapes and Interpolate point position, colors…

Shape Diff----Computes the post-deform or pre-deform difference of two geometries with similar topologies.

Shrinkwrap----Computes the convex hull of the input geometry and moves its polygons inwards along their normals.

Shrinkwrap----Takes the convex hull of input geometry and moves its polygons inwards along their normals.

Skin----Builds a skin surface between any number of shape curves.

Sky----Creates a sky filled with volumentric clouds

Smooth----Smooths out (or "relaxes") polygons, meshes and curves without increasing the number of points.

Smooth----Smooths out (or "relaxes") polygons, meshes and curves without increasing the number of points.

Soft Peak----Moves the selected point along its normal, with smooth rolloff to surrounding points.

Soft Transform----Moves the selected point, with smooth rolloff to surrounding points.

Solid Conform----Creates a tetrahedral mesh that conforms to a connected mesh as much as possible.

Solid Embed----Creates a simple tetrahedral mesh that covers a connected mesh.

Solid Fracture----Creates a partition of a tetrahedral mesh that can be used for finite-element fracturing.

Solver----Allows running a SOP network iteratively over some input geometry, with the output of the network from the previous frame serving as the input for the network at the current frame.

Sort----Reorders points and primitives in different ways, including randomly.

Sphere----Creates a sphere or ovoid surface.

Split----Splits primitives or points into two streams.

Spray Paint----Spray paints random points onto a surface.

Sprite----A SOP node that sets the sprite display for points.

Starburst----Insets points on polygonal faces.

Stash----Caches the input geometry in the node on command, and then uses it as the node’s output.

Stitch----Stretches two curves or surfaces to cover a smooth area.

Stroke----Low level tool for building interactive assets.

Subdivide----Subdivides polygons into smoother, higher-resolution polygons.

Subnetwork----The Subnet op is essentially a way of creating a macro to represent a collection of ops as a single op in the Network Editor.

Super Quad----Generates an isoquadric surface.

Surfsect----Trims or creates profile curves along the intersection lines between NURBS or bezier surfaces.

Sweep----Creates a surface by sweeping cross-sections along a backbone curve.

Switch----Switches between network branches based on an expression or keyframe animation.

TOP SOP----Sends input geometry to a TOP subnet and retrieves the output geometry.

Table Import----Reads a CSV file creating point per row.

Test Geometry: Crag----Creates a rock creature, which can be used as test geometry.

Test Geometry: Pig Head----Creates a pig head, which can be used as test geometry..

Test Geometry: Rubber Toy----Creates a rubber toy, which can be used as test geometry.

Test Geometry: Shader Ball----Creates a shader ball, which can be used to test shaders.

Test Geometry: Squab----Creates a squab, which can be used as test geometry.

Test Geometry: Tommy----Creates a soldier, which can be used as test geometry.

Test Simulation: Crowd Transition----Provides a simple crowd simulation for testing transitions between animation clips.

Test Simulation: Ragdoll----Provides a simple Bullet simulation for testing the behavior of a ragdoll.

Tet Partition----Partitions a given tetrahedron mesh into groups of tets isolated by a given polygon mesh

Tetrahedralize----Performs variations of a Delaunay Tetrahedralization.

TimeShift----Cooks the input at a different time.

Toon Shader Attributes----Sets attributes used by the Toon Color Shader and Toon Outline Shader.

TopoBuild----Lets you interactively draw a reduced quad mesh automatically snapped to existing geometry.

Torus----Creates a torus (doughnut) shaped surface.

Trace----Traces curves from an image file.

Trail----Creates trails behind points.

Transform----The Transform operation transforms the source geometry in "object space" using a transformation matrix.

Transform Axis----Transforms the input geometry relative to a specific axis.

Transform By Attribute----Transforms the input geometry by a point attribute.

Transform Pieces----Transforms input geometry according to transformation attributes on template geometry.

Tri Bezier----Creates a triangular Bezier surface.

TriDivide----Refines triangular meshes using various metrics.

Triangulate 2D----Connects points to form well-shaped triangles.

Trim----Trims away parts of a spline surface defined by a profile curve or untrims previous trims.

Tube----Creates open or closed tubes, cones, or pyramids.

UV Autoseam----Generates an edge group representing suggested seams for flattening a polygon model in UV space.

UV Brush----Adjusts texture coordinates in the UV viewport by painting.

UV Edit----Lets you interactively move UVs in the texture view.

UV Flatten----Creates flattened pieces in texture space from 3D geometry.

UV Flatten----Creates flattened pieces in texture space from 3D geometry.

UV Fuse----Merges UVs.

UV Layout----Packs UV islands efficiently into a limited area.

UV Pelt----Relaxes UVs by pulling them out toward the edges of the texture area.

UV Project----Assigns UVs by projecting them onto the surface from a set direction.

UV Quick Shade----Applies an image file as a textured shader to a surface.

UV Texture----Assigns texture UV coordinates to geometry for use in texture and bump mapping.

UV Transform----Transforms UV texture coordinates on the source geometry.

UV Transform----Transforms UV texture coordinates on the source geometry.

UV Unwrap----Separates UVs into reasonably flat, non-overlapping groups.

Unix----Processes geometry using an external program.

Unpack----Unpacks packed primitives.

Unpack Points----Unpacks points from packed primitives.

VDB----Creates one or more empty/uniform VDB volume primitives.

VDB Activate----Activates voxel regions of a VDB for further processing.

VDB Activate SDF----Expand or contract signed distance fields stored on VDB volume primitives.

VDB Advect----Moves VDBs in the input geometry along a VDB velocity field.

VDB Advect Points----Moves points in the input geometry along a VDB velocity field.

VDB Analysis----Computes an analytic property of a VDB volumes, such as gradient or curvature.

VDB Clip----Clips VDB volume primitives using a bounding box or another VDB as a mask.

VDB Combine----Combines the values of two aligned VDB volumes in various ways.

VDB Diagnostics----Tests VDBs for Bad Values and Repairs.

VDB Fracture----Cuts level set VDB volume primitives into multiple pieces.

VDB LOD----Build an LOD Pyramid from a VDB.

VDB Morph SDF----Blends between source and target SDF VDBs.

VDB Occlusion Mask----Create a mask of the voxels in shadow from a camera for VDB primitives.

VDB Points Delete----Deletes points inside of VDB Points primitives.

VDB Points Group----Manipulates the Internal Groups of a VDB Points Primitive.

VDB Potential Flow----Computes the steady-state air flow around VDB obstacles.

VDB Project Non-Divergent----Removes divergence from a Vector VDB.

VDB Renormalize SDF----Fixes signed distance fields stored in VDB volume primitives.

VDB Resample----Re-samples a VDB volume primitive into a new orientation and/or voxel size.

VDB Reshape SDF----Reshapes signed distance fields in VDB volume primitives.

VDB Segment by Connectivity----Splits SDF VDBs into connected components.

VDB Smooth----Smooths out the values in a VDB volume primitive.

VDB Smooth SDF----Smooths out SDF values in a VDB volume primitive.

VDB Topology to SDF----Creates an SDF VDB based on the active set of another VDB.

VDB Vector Merge----Merges three scalar VDB into one vector VDB.

VDB Vector Split----Splits a vector VDB primitive into three scalar VDB primitives.

VDB Visualize Tree----Replaces a VDB volume with geometry that visualizes its structure.

VDB from Particle Fluid----Generates a signed distance field (SDF) VDB volume representing the surface of a set of particles from a particle fluid simulation.

VDB from Particles----Converts point clouds and/or point attributes into VDB volume primitives.

VDB from Polygons----Converts polygonal surfaces and/or surface attributes into VDB volume primitives.

VDB to Spheres----Fills a VDB volume with adaptively-sized spheres.

Vellum Configure Grain----Configures geometry for Vellum Grain constraints.

Vellum Constraints----Configure constraints on geometry for the Vellum solvers.

Vellum Drape----Vellum solver setup to pre-roll fabric to drape over characters.

Vellum I/O----Packs Vellum simulations, saves them to disk, and loads them back again.

Vellum Pack----Packs Vellum geometry and constraints into a single geometry.

Vellum Post-Process----Applies common post-processing effects to the result of Vellum solves.

Vellum Rest Blend----Blends the current rest values of constraints with a rest state calculated from external geometry.

Vellum Solver----Runs a dynamic Vellum simulation.

Vellum Unpack----Unpacks a Vellum simulation into two outputs.

Verify BSDF----Verify that a bsdf conforms to the required interface.

Vertex----Manually adds or edits attributes on vertices (rather than on points).

Vertex Split----Takes a vertex attribute and splits any point whose vertices differ by more than a specified tolerance at that attribute.

Visibility----Shows/hides primitives in the 3D viewer and UV editor.

Visualize----Lets you attach visualizations to different nodes in a geometry network.

Volume----Creates a volume primitive.

Volume Analysis----Computes analytic properties of volumes.

Volume Arrival Time----Computes a speed-defined travel time from source points to voxels.

Volume Blur----Blurs the voxels of a volume.

Volume Bound----Bounds voxel data.

Volume Break----Cuts polygonal objects using a signed distance field volume.

Volume Compress----Re-compresses Volume Primitives.

Volume Convolve 3×3×3----Convolves a volume by a 3×3×3 kernel.

Volume FFT----Compute the Fast Fourier Transform of volumes.

Volume Feather----Feathers the edges of volumes.

Volume Merge----Flattens many volumes into one volume.

Volume Mix----Combines the scalar fields of volume primitives.

Volume Optical Flow----Translates the motion between two "image" volumes into displacement vectors.

Volume Patch----Fill in a region of a volume with features from another volume.

Volume Ramp----Remaps a volume according to a ramp.

Volume Rasterize----Rasterizes into a volume.

Volume Rasterize Attributes---Samples point attributes into VDBs.

Volume Rasterize Curve----Converts a curve into a volume.

Volume Rasterize Hair----Converts fur or hair to a volume for rendering.

Volume Rasterize Particles----Converts a point cloud into a volume.

Volume Rasterize Points----Converts a point cloud into a volume.

Volume Reduce----Reduces the values of a volume into a single number.

Volume Resample----Resamples the voxels of a volume to a new resolution.

Volume Resize----Resizes the bounds of a volume without changing voxels.

Volume SDF----Builds a Signed Distance Field from an isocontour of a volume.

Volume Slice----Extracts 2d slices from volumes.

Volume Splice----Splices overlapping volume primitives together.

Volume Stamp----Stamps volumes instanced on points into a single target volume.

Volume Surface----Adaptively surfaces a volume hierarchy with a regular triangle mesh.

Volume Trail----Computes a trail of points through a velocity volume.

Volume VOP----Runs CVEX on a set of volume primitives.

Volume Velocity----Computes a velocity volume.

Volume Velocity from Curves----Generates a volume velocity field using curve tangents.

Volume Velocity from Surface----Generates a velocity field within a surface geometry.

Volume Visualization----Adjusts attributes for multi-volume visualization.

Volume Wrangle----Runs a VEX snippet to modify voxel values in a volume.

Volume from Attribute----Sets the voxels of a volume from point attributes.

Voronoi Fracture----Fractures the input geometry by performing a Voronoi decomposition of space around the input cell points

Voronoi Fracture----Fractures the input geometry by performing a Voronoi decomposition of space around the input cell points

Voronoi Fracture Points----Given an object and points of impact on the object, this SOP generates a set of points that can be used as input to the Voronoi Fracture SOP to simulate fracturing the object from those impacts.

Voronoi Split----Cuts the geometry into small pieces according to a set of cuts defined by polylines.

Vortex Force Attributes----Creates the point attributes needed to create a Vortex Force DOP.

Whitewater Source----Generates volumes to be used as sources in a whitewater simulation.

Whitewater Source----Generates emission particles and volumes to be used as sources in a Whitewater simulation.

Winding Number----Computes generalized winding number of surface at query points.

Wire Blend----Morphs between curve shapes while maintaining curve length.

Wire Capture----Captures surfaces to a wire, allowing you to edit the wire to deform the surface.

Wire Deform----Deforms geometry captured to a curve via the Wire Capture node.

Wire Transfer----Transfers the shape of one curve to another.

Wireframe----Constructs polygonal tubes around polylines, creating renderable geometry.

glTF ROP output driver

posescope----Assigns channel paths and/or pickscripts to geometry.




===============================================================================


================================VEX networks========================================



CVEX Type----This network defines a CVEX shader (SHOP).

RSL Displacement Shader----Creates a RenderMan RSL displacement shader.

RSL Imager Shader----Creates a RenderMan RSL imager shader.

RSL Light Shader----Creates a RenderMan RSL light shader.

RSL Surface Shader----Creates a RenderMan RSL surface shader.

RSL Volume Shader----Creates a RenderMan RSL volume shader.

VEX Compositing Filter----This network defines a COP operator type that requires at least one input.

VEX Compositing Generator----This network defines a COP operator type that takes no inputs.

VEX Displacement Shader----This network defines a SHOP operator type.

VEX Fog Shader----This network defines a SHOP operator type.

VEX Geometry Operator----This network defines a surface node (SOP).

VEX Image3D Shader----This network defines a SHOP operator type.

VEX Light Shader----This network defines a SHOP operator type.

VEX Motion and Audio Operator----This network defines a CHOP operator type.

VEX Particle Operator----This network defines a POP operator type.

VEX Photon Shader----This network defines a SHOP operator type.

VEX Shadow Shader----This network defines a SHOP operator type.

VEX Subnetwork----This network contains other VOP networks.

VEX Surface Shader----This network defines a SHOP operator type.





==================================================================================


==================================TOP nodes

Attribute Copy-----Copies attributes from work items in one branch onto work items in another branch.

Attribute Create----Creates or sets an attribute on all incoming work items.

Attribute Delete----Removes attributes from work items.

Attribute from String----Parses attribute values from a string, such as a file name.

Block Begin Feedback----Starts a feedback loop. TOP nodes within the block execute serially, optionally looping for each incoming work item.

Block End Feedback----Ends a feedback loop. TOP nodes within the block execute serially, optionally looping for each incoming work item.

CSV Input----Copies data from a CSV file into work item attributes.

CSV Output----Writes work item attributes to a CSV file.

Command Send----Sends code to a shared server to execute

Command Server End----Ends a command server block.

Deadline Scheduler----PDG Scheduler for Thinkbox’s Deadline software.

Download File----Downloads the contents of one or more URLs into files.

Environment Edit----Edits the variables set in the environment work item command lines execute in.

Error Handler----Error handler for failed work items.

FFmpeg Encode Video----Encodes a sequence of still images as a video file.

FFmpeg Extract Images----Extracts a sequence of still images from a video file.

File Compress----Compress files into an archive.

File Copy----Copies a file from one location to another, either at runtime or whenever the node generates.

File Decompress----Decompresses archive files specified by incoming work items into individual files.

File Pattern----Creates work items based on files that match a certain pattern.

File Remove----Deletes a file at a specified path.

File Rename----Renames or moves a file.

Filter By Expression----Conditionally filter upstream work items

Generic Generator----Generates work items with no attributes that run a command line.

Generic Server Begin----Starts a generic command server.

Geometry Import----Load points or primitives from SOP or file geometry into work item attributes or a temporary file.

HDA Processor----Creates work items that cook a digital asset

HQueue Scheduler----Schedules work items using HQueue.

Houdini Server Begin----Starts a persistent Houdini command server

ImageMagick----Provides easy access to ImageMagick functionality such as mass image convert, resize, and image mosaics.

Invoke----Invokes a compiled block on input geometry

Json Input----Extracts data from JSON files and creates attributes

Json Output----Performs various operations that produce JSON output

Local Scheduler----Schedules work items on the local machine.

Make Directory

Map All----Maps all upstream work items to downstream work items.

Map by Expression----Maps upstream work items to downstream work items using an expression

Map by Index----Maps upstream work items to downstream work items based on their index.

Map by Range----Map upstream work items to downstream work items using range values

Maya Server Begin----Starts a persistent Maya command server

Merge----Merge all upstream work items

Null----Does nothing

OP Notify----Notify an OP node that some TOP work has completed

Output----Subnet output

Partition by Attribute----artitions work items based on their attributes

Partition by Bounds----Partitions source items spatially using the bounding items.

Partition by Combination----Partitions work items into pairs, triples, etc

Partition by Comparison----Partitions work items using existing comparisons

Partition by Expression----Partitions work items based on an expression

Partition by Frame----Partitions work items based on their frame

Partition by Index----Partitions work items based on their index

Partition by Node----Partitions work items based on their node

Partition by Range----Partition work items based on range values

Partition by Tile----Partitions work items spatially using axis-aligned bounding boxes.

Perforce----Execute Perforce commands through PDG

Python Mapper----Maps work items using a Python script

Python Partitioner----Partitions work items using a Python script

Python Processor----Generate work items using a Python script

Python Scheduler----A Python-based programmable Scheduler for PDG.

Python Script----Creates work items that run a script

ROP Alembic Output----Creates work items that cook an embedded ROP Alembic node

ROP Composite Output----Creates work items that cook an embedded ROP Composite node

ROP Fetch----Creates work items that cook a ROP node or network

ROP Geometry Output----Creates work items that cook an embedded ROP Geometry node

ROP Mantra Render----Creates work items that cook an embedded ROP Mantra node

Render IFD----Creates work items that render an IFD with Mantra

SQL Input

SQL Output

Send Email----Sends an email

Shotgun Create----Create a Shotgun entity.

Shotgun Download----Download an attachment from Shotgun.

Shotgun Find----Find a Shotgun entity.

Shotgun New Version----Create a new Version with an attachment.

Shotgun Session----Start a session to connect to a Shotgun instance.

Shotgun Update----Update fields on an existing Shotgun entity.

Shotgun Upload----Create an attachment in Shotgun.

Sort----Sorts work items by a list of attributes

Split----Splits upstream items in two

Switch----Switch which between network branches

TOP Fetch----Cooks another TOP network

TOP Fetch Input----Input to a TOP fetch-ed network

Text to CSV----Converts some plain text to CSV

Tractor Scheduler----Schedules work items using Pixar’s Tractor.

Wait for All----Waits for all upstream work items to complete.

Wedge----Creates work items with varying attribute values.

Work Item Expand----Expands file lists or partitions into multiple work items

Xml Input----Extracts data from an XML file and creates a string attribute containing the data





==================================================================================


====================================VOP nodes =====================================



Absolute----Computes the absolute value of the argument.

Add----Outputs the sum of its inputs.

Add Attribute----Adds a new attribute.

Add Constant----Adds the specified constant value to the incoming integer, float, vector or vector4 value.

Add Point----Adds points to the geometry.

Add Point to Group----Adds the point specified to the group given.

Add Primitive----Adds primitives to the geometry.

Add Steer Force----Multiply steerforce by steerweight attributes and normalize results by total steerweight.

Add Vertex----Adds vertices to the geometry.

Add Wind Force----Layers a wind force onto a simulation.

Advect by Volumes----Advects a position by a set of volume primitives stored in a disk file.

Agent Clip Catalog----Returns all of the animation clips that have been loaded for an agent primitive.

Agent Clip Length----Returns the length (in seconds) of an agent’s animation clip.

Agent Clip Names----Returns an agent primitive’s current animation clips.

Agent Clip Sample----Samples an agent’s animation clip at a specific time.

Agent Clip Sample Rate----Returns the sample rate of an agent’s animation clip.

Agent Clip Times----Returns the current times for an agent primitive’s animation clips.

Agent Clip Weights----Returns the blend weights for an agent primitive’s animation clips.

Agent Convert Transforms----Converts transforms between local space and world space for an agent primitive.

Agent Layer Bindings----Returns the transform that each shape in an agent’s layer is bound to.

Agent Layer Name----Returns the name of the current layer or collision layer of an agent.

Agent Layer Shapes----Returns the names of the shapes referenced by an agent primitive’s layer.

Agent Layers----Returns all of the layers that have been loaded for an agent primitive.

Agent Rig Children----Returns the child transforms of a transform in an agent primitive’s rig.

Agent Rig Find----Finds the index of a transform in an agent primitive’s rig.

Agent Rig Parent----Returns the parent transform of a transform in an agent primitive’s rig.

Agent Transform Count----Returns the number of transforms in an agent primitive’s rig.

Agent Transform Names----Returns the name of each transform in an agent primitive’s rig.

Agent Transforms----Returns the current local or world space transforms of an agent primitive.

Align----Computes a matrix representing the rotation around the axes normal to two vectors by the angle which is between the two vectors.

Alpha Mix----Takes two values for alpha based on the surface orientation relative to the camera and blends between the two with a rolloff as the bias control, effectively removing the silhouettes of the geometry edges.

Ambient----Generates a color using ambient lighting model calculation.

And----Performs a logical "and" operation between its inputs and returns 1 or 0.

Anti-Aliased Flow Noise----Generates anti-aliased (fractional brownian motion) noise by using the derivative information of the incoming position to compute band-limited noise.

Anti-Aliased Noise----Generates anti-aliased noise by using the derivative information of the incoming position to compute band-limited noise.

Anti-Aliased Ramp Parameter

Append----Adds an item to an array or string.

Arctangent----Performs the atan2() function

Array Contains----Checks whether a value exists in an array.

Array Find Index----Finds the first location of an item in an array or string.

Array Find Indices----Finds all locations of an item in an array or string.

Array Length----Produces the length of an array.

Attenuated Falloff----Computes attenuated falloff.

Average----Outputs the average of its inputs.

Average Vector Component----Computes the average value of a vector argument.

BSDF Tint----Tints a BSDF with separate control over colorization and luminance.

Bake Exports----Export shading for use in bake image planes

Bias

Bind----Represents an attribute bound to VEX.

Blend Regions----Takes a float input as a bias to blend between three input regions.

Block Begin----Marks the start of a code block.

Block Begin For----Marks the start of a for loop block.

Block Begin For-Each----Marks the start of a for-each loop block.

Block Begin If----Marks the start of an if code block.

Block End----Marks the end of a code block.

Block End Break-If----Marks the end of a code block.

Block End While----Marks the end of a while code block.

Bounding Box----Returns two vectors representing the minimum and maximum corners of the bounding box for the specified geometry.

Box Clip----Clips the line segment defined by p1 and p2 to the bounding box specified by the min and max corner points.

Boxes----Generates repeating filtered squares.

Bricker----Generates a brick pattern based on the parametric s and t coordinates.

Brushed Circles----Outputs an angle that gives the appearance of a circular brush pattern when used with anisotropy direction.

Brushed Metal Shader----A basic brushed metal shader.

Build Array----Outputs the array consisting of its inputs as array elements.

Bump Noise----Displaces surfaces along their normal using anti-aliased noise, and returns the displaced surface position, normal, and displacement amount.

Bump To Normal Map----Compute a tangent-space normal map from a bump map

Burlap----Generates a burlap displacement pattern useful for simulating rough cloth or weave patterns.

Burlap Pattern----Returns float between 0 and 1 which defines a burlap pattern useful for simulating rough cloth or weave patterns.

COP Input----Returns a pixel value in one of the 4 input COPs connected to the VEX COP.

CVEX Shader Builder----A node that implements a CVEX shader using its children VOPs.

Car Paint Shader----Simulates car paint with embedded metallic flakes and a coat layer.

Cavities----Produces a surface displacement that simulates small surface damage using anti-aliased noise of various frequencies.

Ceiling----Returns the smallest integer greater than or equal to the argument.

Cellular Cracks----Generates a cellular crack displacement suitable for simulating skin, leather, dried earth, and all kinds of crusts.

Cellular Noise----Computes 2D, anti-aliased cellular noise suitable for shading.

Character to String----Converts an unicode codepoint to a UTF8 string.

Checkered----Returns number between 0 and 1 which defines a checkered pattern useful for visualizing parametric or texture coordinates.

Clamp----Clamps the input data between the minimum and maximum values.

Class Cast----Downcasts a generic (anonymous) co-shader object to a specific co-shader

Classic Shader----Flexible material including multiple reflection layers, subsurface scattering, refractions and displacement.

Classic Shader Core----A powerful, highly flexible, generic surface shader with displacement.

Collect

Color Correction----Provides a means to change the hue, saturation, intensity, bias, gain and gamma of the input color.

Color Map----Looks up a single sample of RGB or RGBA color from a disk image.

Color Mix----Computes a blend (or a mix) of its two color inputs, and outputs the resulting color.

Color Transform

Compare----Compares two values and returns true or false.

Complement----Computes the complement of the argument by subtracting the argument from 1.

Composite

Compute Lighting----Computes lighting using Physically Based Rendering.

Compute Normal----This node gives finer control over handling of the normal attribute in VOPs.

Compute Tangents----Compute surface tangents in different ways.

Conductor Fresnel----Outputs a physically correct reflection factor for conductive materials.

Conserve Energy----Clamp the reflectivity of a bsdf to 1.

Constant----Outputs a constant value of any VEX data type.

Contour----Increases or decreases contrast for values at the bottom of the input range.

Copy----Takes a single input of any data type.

Cosine----Performs a cosine function.

Crackle----Returns float between 0 and 1 which defines a crackle pattern useful for simulating the fine grain texture in skin or on a much larger scale dried mudflats.

Create Point Group----Creates a new point group with the name specified.

Cross Product----Computes the cross product between two vectors, defined as the vector perpendicular to both input vectors.

Curl Noise----Creates divergence-free 3D noise using a curl function.

Curl Noise 2D----Creates divergence-free 2D noise using a curl function.

Curvature----Computes surface curvature.

Decal----An OTL that performs composting of texture maps.

Degrees to Radians----Converts degrees to radians.

Delayed Load Procedural

Delayed Read Archive

Depth Map----Works on an image which was rendered as a z-depth image, returning the distance from the camera to the pixel (or plane) in question.

Determinant----Computes the determinant of a 4×4 or 3×3 matrix.

Direct Lighting----Internal VOP used to compute direct lighting.

Displace----Displaces surface position and modifies surface normals.

Displace Along Normal----Displaces the surface along the surface normal by a given amount.

Displacement Texture----Modifies normals and/or positions based on a texture map.

Distance----Returns the distance between two 3D or 4D points.

Distance Point to Line----Returns the closest distance between a point and a line segment defined by two end points.

Divide----Outputs the result of dividing each input value by the next.

Divide Constant----Divides the incoming integer, float, vector or vector4 value by the specified constant value.

Dot Product----Computes the dot product between two vectors.

Dual Rest----Outputs sanitized dual rest values based.

Dual Rest Solver----Sanitizes dual rest attribute data for easier use.

Edge Falloff----Creates a smooth roll-off of the input color from the center of the geometry to the edges, based on the surface normal.

Eggshell Pattern----Returns a new surface normal (N) which has a slight fine grained bump on it.

Eigenvalues

Ends With----Result 1 if the string ends with the specified string.

Environment Map----Sets the environment map (on an infinite sphere) and returns its color.

Euler to Quaternion----Builds a quaternion with the given euler rotation.

Exponential----Computes the exponential function of the argument.

Extract Transform----Extracts the translation, rotation, scale or shear component of a 4×4 transform matrix.

Fake Caustics----Outputs and opacity value which can be used to approximate caustic lighting effects.

Fast Shadow----Sends a ray from the position P along the direction specified by the direction D.

Field Name----Provides a "fallback" value for a field/attribute if the field does not exist or the given field name is an empty string.

Field Parameter----Provides a "fallback" value for a field/attribute if the field does not exist or the given field name is an empty string.

Filament Sample

Filter Pulse Train

Filters the input.

Filter Shadow----Sends a ray from the position P along the direction specified by the direction D, a…

Filter Step----Computes the anti-aliased weight of the step function.

Filter Width----This function returns the square root of the area of a 3D input or the length of the derivative of a float input, such as s or t.

Find Attribute Value

Find Attribute Value Count

Find Attribute Value by Index

Fit Range----Takes the value in the source range and shifts it to the corresponding value in the destination range.

Fit Range (Unclamped)----Takes the value in the source range and shifts it to the corresponding value in the destination range.

Float to Integer----Converts a float value to an integer value.

Float to Matrix----Converts sixteen floating-point values to a 4×4 matrix value.

Float to Matrix2----Converts four floating-point values to a matrix2 value.

Float to Matrix3----Converts nine floating-point values to a matrix3 value.

Float to Vector----Converts three floating-point values to a vector value.

Float to Vector2----Converts two floating-point values to a vector2 value.

Float to Vector4----Converts four floating-point values to a vector4 value.

Floor----Returns the largest integer less than or equal to the argument.

Flow Noise----Generates 1D and 3D Perlin Flow Noise from 3D and 4D data.

Fraction----Computes the fractional component of the argument.

Fresnel----Computes the Fresnel reflection/refraction contributions given a normalized incident ray, a normalized surface normal, and an index of refraction.

From NDC----Transforms a position from normal device coordinates to the coordinates in the appropriate space.

From NDC----Transforms a position from normal device coordinates to the coordinates in the appropriate space.

From Polar----Converts polar coordinates to cartesian coordinates.

Front Face----Returns the front facing normal of a surface, given a surface normal (N) and an incident ray (I).

Fur Guide Global Variables----Provides outputs representing commonly used input variables of fur guide shader network.

Fur Guide Output Variables and Parameters----Provides inputs representing the output variables of a fur guide shader network.

Fur Procedural----Creates a set of hair-like curves across a surface at render time.

Fur Skin Global Variables----Provides outputs representing commonly used input variables of fur skin shader network.

Fur Skin Output Variables and Parameters----Provides inputs representing the output variables of a fur skin shader network.

Furrows----Displaces the surface along the surface normal by an amount equal to the value of an anti-aliased cosine wave.

Fuzzy And----Performs a fuzzy "and" operation between its inputs and returns a value between 0 and 1.

Fuzzy Defuzz----Performs a defuzzify operation between its input fuzzy sets and returns a crisp value.

Fuzzy Inference----Performs a fuzzy inference operation over each input to determine the truth of the fuzzy set defined on this node.

Fuzzy Inference Mirror----"This node represents two inferred fuzzy sets that are mirrors of one another.

Fuzzy Input----Performs a "fuzzify" operation that calculates a fuzzy value given a membership function and an input crisp value.

Fuzzy Not----This operator performs a fuzzy not operation on an integer or float value.

Fuzzy Obstacle Sense----Detects obstacles in an agent’s field of view.

Fuzzy Or----Performs a fuzzy "or" operation between its inputs and returns a value between 0 and 1.

Gain

Gather Loop----Sends rays into the scene and contains a subnetwork of VOPs to operate on the information gathered from the shaders of surfaces hit by the rays.

Gaussian Random----Generates a random number fitting a Gaussian distribution.

Gaussian Random UV----Generates a random number fitting a Gaussian distribution.

General Fresnel----Computes the Fresnel reflection/refraction contributions and vectors for objects with or without depth.

Generic Shader----Represents a shader.

Geometry VOP Global Parameters----Provides outputs that represent all the global variables for the Attribute VOP network types.

Geometry VOP Output Variables----Simple output variable for Geometry VOP Networks.

Get Attribute

Get BSDF Albedo----Compute the reflectivity of a bsdf.

Get Blur P

Get CHOP Attribute----Returns a CHOP attribute value in one of the 4 input CHOPs connected to the Channel VOP.

Get Channel Transform----Returns a transform value built from 9 channels from one of the 4 input CHOPs connected to the Channel VOP.

Get Channel Value----Returns a sample value in one of the 4 input CHOPs connected to the Channel VOP.

Get Channel Value by Name----Returns a sample value in one of the 4 input CHOPs connected to the Channel VOP.

Get Element----Gets a specified element from array.

Get Layer Export----Obtains a value of the export variable added to the Shader Layer struct.

Get Matrix Component----Extracts a 4×4 matrix component.

Get Matrix2 Component----Extracts a 2×2 matrix3 component.

Get Matrix3 Component----Extracts a 3×3 matrix3 component.

Get Object Transform----Gets the transform matrix of a named object in camera (current) space.

Get PTexture ID

Get Primitive ID

Get Vector Component----Extracts a vector component.

Get Vector2 Component----Extracts a vector2 component.

Get Vector4 Component----Extracts a vector4 component.

Get a CHOP Channel Value----Evaluates a CHOP channel and return its value.

Get a Channel or Parameter Value----Evaluates a channel (or parameter) and return its value.

Get an Object Transform----Evaluates an OBJ node’s transform

Gingham Checks----Generates anti-aliased gingham checks similar to a tablecloth pattern.

Global Variables----Provides outputs that represent all the global variables for the current VOP network type.

Gradient 3D----Returns the gradient of a single channel 3D texture image at a specified position within that image.

HSV to RGB----Converts HSV color space to RGB color space.

Hair Normal----Generates a normal vector which always faces the camera, parallel to the incidence vector.

Hair Shader----A powerful, highly flexible, general model for hair/fur shading.

Has Input----Returns 1 if the specified input (0-3) is connected.

High-Low Noise----Computes a mix of high and low frequency, anti-aliased noise with a wide range of applications.

Houdini Engine Procedural: Curve Generate----Cooks a SOP asset for each point in the source geometry and instances the generated curves onto the point.

Houdini Engine Procedural: Point Generate----Cooks a SOP asset for each point in the source geometry and instances the generated points onto the point.

Hue Shift----Uses the shift value to move the hue of the input color along the color wheel by the amount influenced by the amplitude.

If Connected----Passes through the value of the first input if the first input is ultimately connected.

Illuminance Loop----Only available in Surface VOP networks.

Image 3D Iso-Texture Procedural----This procedural will generate an iso-surface from a 3D texture image (.i3d file).

Image 3D Volume Procedural----This procedural will generate a volume from a 3D texture image (.i3d file).

Import Attribute----Imports attribute data from the OP connected to the given input.

Import Detail Attribute

Import Displacement Variable----Imports the value of the specified variable from a displacement shader and stores it in var.

Import Light Variable----Imports the value of the specified variable from a light shader and stores it in var.

Import Point Attribute

Import Primitive Attribute

Import Properties from OpenColorIO----Imports a color space property from Open Color IO.

Import Ray Variable----Imports the value of the specified variable sent from a trace() function and stores it in var.

Import Surface Variable----Imports the value of the specified variable from a surface shader and stores it in var.

Import Vertex Attribute

In Group----Returns 1 if the point or primitive is in the group specified by the string.

Indirect Lighting----Internal VOP used to compute indirect lighting.

Inline Code----Write VEX code that is put directly into your shader or operator definition.

Insert----Inserts an item, array, or string into an array or string.

Instance with Hscript Procedural----Runs hscript for each point in the source geometry and instances the generated geometry to the point.

Integer to Float----Converts an integer value to a float value.

Integer to Vector

Intersect----Computes the intersection of a ray with geometry.

Intersect All----Computes all the intersections of a ray with geometry.

Invert----If given a 3×3 or 4×4 matrix, this operator computes its inverse (or just returns the input matrix if it detects singularity).

Irradiance----Computes the irradiance (the global illumination) at the point P with the normal N.

Is Alphabetic----Result 1 if all the characters in the string are alphabetic.

Is Connected----Outputs 1 if the input is ultimately connected, otherwise it outputs 0.

Is Digit----Result 1 if all the characters in the string are numeric.

Is Finite----Returns 1 if the number is a normal number, ie, not infinite or NAN.

Is Fog Ray----Returns 1 if the shader is being evaluated from within a fog shader.

Is Front Face----Returns true if the normal of the surface is forward facing, and false if it isn’t.

Is NAN----Returns 1 if the number is not a number.

Is Shadow Ray----Returns 1 if the shader is being evaluated for shadow rays.

Jittered Hair Normal

Join Strings----Concatenate all the strings of an array inserting a common spacer.

Lambert----Generates a color using the Lambert diffuse lighting model calculation.

Layer Composite----Combines two layers using standard compositing operations.

Layer Mix----Outputs a mix of the two input layers, blended using the alpha value.

Length----Computes the length of an array

Length----Computes the length of a 3D or 4D vector.

Lighting Model----Performs a lighting model calculation to generate a color.

Limits----Selectively clamps values to a minimum and/or maximum value.

Logarithm----Computes the natural logarithm function of the argument.

Look At----Computes a 3×3 rotation matrix to orient the z-axis along the vector (to - from) under the transformation.

Luminance----Computes the luminance of the RGB color specified by the input parameter.

Make Instance Transform----Builds a general 4×4 transform matrix derived from the standard copy/instance attributes

Make Space Transform----Returns the transformation matrix to transform from a transform space such as an object’s transform space to another space, such as world space.

Make Transform----Builds a general 4×4 transform matrix.

Mandelbrot Set----Generates a Mandelbrot pattern.

Material shader builder----A higher-level shader that can contain one or more sub-shaders, such as surface shaders, displacement shaders, and rendering properties.

Matrix to Float----Unpacks a 4×4 matrix into its sixteen components.

Matrix to Vector4----Unpacks a 4×4 matrix into its rows.

Matrix2 to Float----Unpacks a 2×2 matrix2 into its four components.

Matrix2 to Matrix3----Converts a 2×2 matrix to a 3×3 matrix.

Matrix2 to Matrix4----Converts a 2×2 matrix to a 4×4 matrix.

Matrix2 to Vector2----Unpacks a 2×2 matrix into its rows.

Matrix3 to Float----Unpacks a 3×3 matrix3 into its nine components.

Matrix3 to Matrix2----Converts a 3×3 matrix to a 2×2 matrix.

Matrix3 to Matrix4

Matrix3 to Quaternion----Converts a matrix3, representing a rotation, to a quaternion representing the same rotation.

Matrix3 to Vector----Unpacks a 3×3 matrix into its rows.

Matrix4 to Matrix2----Converts a 4×4 matrix to a 2×2 matrix.

Matrix4 to Matrix3

Matte----Implements a matte shader that occludes geometry behind the surface being rendered.

Max Vector Component----Computes the maximum value of a vector argument.

Maximum----Outputs the maximum value from its inputs.

Meta-Loop Import----Takes a handle generated by the Meta-Loop Start operator and will import attributes…

Meta-Loop Next----Takes a handle generated by the Meta-Loop Start operator and will "iterate" to the …

Meta-Loop Start----Opens a geometry file and initializes the handle to iterate through all metaballs at the position specified.

Metaball Attribute----Returns the value of the given point attribute at the specified position in the metaball field.

Metaball Density----Returns the density of the metaball field at the specified position.

Metaball Space----Transforms the specified position into the local space of the metaball.

Metaball Weight----Returns the metaweight of the geometry at a given position.

Metadata----Returns true if the specified metadata exists.

Metadata----Returns metadata from one of the 4 input COPs connected to the VEX COP.

Method----Represents a method inside a class-based shader.

Method Call----Invokes a given method on a given struct or co-shader object.

Method Input----Represents a method argument list inside a class-based shader.

Method Subner----Represents a method inside a class-based shader.

Min Vector Component----Computes the minimum value of a vector argument.

Minimum----Outputs the minimum value from its inputs.

Minimum Position----Finds closest position on a primitive in a given geometry file.

Mix----Computes a blend (or a mix) of its input values using linear interpolation.

Modulo----Computes the modulo of two values.

Multiply----Outputs the product of its inputs.

Multiply Add Constant----Will take the input value, add the pre-add amount, multiply by the constant multiplier, then add the post-add amount.

Multiply Constant----Multiplies the incoming value by a constant.

Near Point----Finds closest point in a given geometry file.

Negate----Negates the incoming integer, float, vector or vector4 value.

Neighbor Count File----Count the number of connected points from a given point in a given geometry file (or op:path)

Neighbor File----Finds the nth neighbouring point for a given point in a given geometry file.

Neighbors----Retrieves an array of indices to the points connected to the given point.

Non-Deterministic Random----A non-deterministic random number generator.

Normal Clamp----Clamp shading normals to prevent bad reflection directions

Normal Falloff----Generates a falloff value based on the relationship between the normal and incident vectors.

Normalize----Normalizes a vector.

Not----This operator performs a logical not operation on an integer value, returning 1 if the input is zero, and 0 if the input is non-zero.

Null----Passes the inputs to the output with an optional name change.

OCIO Color Transform----Transforms color spaces using Open Color IO.

OSL Bias

OSL Calculate Normal

OSL Dx/Dy/Dz

OSL Environment Map

OSL Gain

OSL Logarithm

OSL Shader----Implements an OSL shader.

OSL Step

OSL Texture Map

OSL Transform

OSL Transform Color

Occlusion----Computes ambient occlusion at the point P with the normal N.

Ocean Sample Layers----Sample ocean values from layered ocean spectra at the specified position and time.

OpenSubdiv Face Count----Returns the number of coarse faces in the subdivision hull

OpenSubdiv First Patch----Returns the patch of the first patch for a given face in the subdivision hull.

OpenSubdiv Limit Surface----Evaluates a point attribute on the limit of a subdivision surface.

OpenSubdiv Lookup Face----Outputs the Houdini face and UV coordinates corresponding to the given coordinates on an OSD patch.

OpenSubdiv Lookup Patch----Outputs the OSD patch and UV coordinates corresponding to the given coordinates on a Houdini polygon face.

OpenSubdiv Patch Count----Returns the number of patches in the subdivision hull

Or----This operator performs a logical "or" operation between its inputs and returns 1 or 0 .

Oren-Nayar----Generates a color using the Oren-Nayar diffuse lighting model calculation.

Orient----Reorients a vector representing a direction by multiplying it by a 4×4 transform matrix.

Oscillations----Returns an anti-aliased cosine or sine wave.

Outer Product----Computes the outer product of a pair of vectors.

Output Variables and Parameters----Provides inputs representing the writable output variables of the shader network.

PBR Emission----Makes a shaded surface emissive.

PBR Hair Primary Reflection----Produce a hair BSDF.

PBR Hair Secondary Reflection----Produce a hair BSDF.

PBR Hair Transmission----Produce a hair BSDF.

PBR Lighting----Evaluate Lighting Using PBR.

PBR Metallic Reflection----Computes metallic reflections.

PBR Non-Metallic----Computes reflections and refractions for dielectric (non-metallic) materials.

PBR SSS----Creates an approximate SSS BSDF.

PBR Single Scatter----Creates a Single Subsurface Scatter BSDF.

PBR Volume Phase Function

PRB Diffuse----Produce a normalized diffuse bsdf.

Parameter----Represents a user-controllable parameter.

Periodic Noise----Generates 1D and 3D Perlin noise from 1D, 3D and 4D data.

Periodic Worley Noise----Computes 1D, 3D, and 4D tileable Worley noise, which is synonymous with "cell noise".

Photon Output Variables----Performs photon russian roulette.

Physical SSS----Outputs surface color based on a physically-based subsurface scattering model. This node an do physically correct single scattering and/or multiple scattering.

Pixel Area----Returns the area of the current pixel after being transformed to the new UV coordinate uvpos.

Pixel Derivative----Returns U and V derivatives of the current pixel.

Plane Clip----Clips the line segment defined by p1 and p2 against the 3D plane defined by the following equation: plane.

Plane Count----Returns the number of planes in the input.

Plane Exists----Returns the name of the plane with the index plane_index in input input_index.

Plane Index----Returns the index of the plane with the name plane_index in input input_index.

Plane Name----Returns the name of the plane with the index plane_index in input input_index.

Plane Size----Returns the number of components in the plane with the index plane_index in input input_index.

Point Bounding Box----Returns two vectors representing the minimum and maximum corners of the bounding box for the specified geometry.

Point Cloud Close----This node closes a point cloud handle opened by pcopen.

Point Cloud Export----This node exports point data while inside a pcunshaded loop.

Point Cloud Farthest----This node finds the farthest query point produced by pcopen.

Point Cloud Filter----This node filters the points queried by pcopen.

Point Cloud Find----Returns a list of closest points from a file

Point Cloud Find Radius----Returns a list of closest points from a file taking into account their radii.

Point Cloud Import----This node imports point data while inside a pciterate or pcunshaded loop.

Point Cloud Import by Index----This node imports point data from a pcopen.

Point Cloud Iterate----This node advances to the next iteration point returned by pcopen.

Point Cloud Num Found----This node returns the number of points found by pcopen.

Point Cloud Open----This node opens a point cloud file and searches for points around a source position.

Point Cloud Unshaded----This node advances to the next unshaded iteration point returned by pcopen.

Point Cloud Write----This function writes data for the current shading point out to a point cloud file.

Point Count----Returns the number of points for all primitives in the given geometry.

Point In Group----Returns 1 if the point specified by the point number is in the group specified by the string.

Point Instance Procedural----The underlying procedural when using Fast Point Instancing with the instance render parameters.

Point Loop----Only available in Image3D VOP networks.

Point Replicate----The Point Replicate Procedural takes a number of input points and multiplies them, and processes the result using a CVEX script.

Pop----Removes the last element of an array and returns it.

Power----Raises the first argument to the power of the second argument.

Primitive Attribute----Evaluates an attribute for a given primitive at the specified uv parametric location.

Primitive Intrinsic----Evaluates an intrinsic on a given primitive.

Primitive Normal----Returns the normal of a primitive (defined by its number) at the given uv parametric location.

Principled Shader----An artist-friendly shader that can model a large number of materials realistically.

Principled Shader----An artist-friendly shader that can model a large number of materials realistically.

Print----Generate a formatted text string.

Promote Layer Exports----Promotes the export variables from the Shader Layer struct to the parent shader

Properties

Pxr AOV Light----Pxr AOV Light shader

Pxr Adjust Normal----Pxr Adjust Normal shader

Pxr Area Light----Pxr Std Area Light light shader

Pxr Attribute----Pxr Attribute shader

Pxr Background Display Filter----Pxr Background Display Filter shader

Pxr Background Sample Filter----Pxr Background Sample Filter shader

Pxr Bake Point Cloud----Pxr Bake Point Cloud shader

Pxr Bake Texture----Pxr Bake Texture shader

Pxr Barn Light Filter----Pxr Barn Light Filter shader

Pxr Black----Pxr Black shader

Pxr Black Body----Pxr Black Body pattern shader

Pxr Blend----Pxr Blend shader

Pxr Blocker----Pxr Blocker light filter shader

Pxr Blocker Light Filter----Pxr Blocker Light Filter shader

Pxr Bump----Pxr Bump shader

Pxr Bump Manifold 2d----Pxr Bump Manifold 2d shader

Pxr Camera----Pxr Camera shader

Pxr Checker----Pxr Checker shader

Pxr Clamp----Pxr Clamp shader

Pxr Color Correct----Pxr Color Correct shader

Pxr Combiner Light Filter----Pxr Combiner Light Filter shader

Pxr Constant----Pxr Constant shader

Pxr Cookie Light Filter----Pxr Cookie Light Filter shader

Pxr Copy AOV Display Filter----Pxr Copy AOV Display Filter shader

Pxr Copy AOV Sample Filter----Pxr Copy AOV Sample Filter shader

Pxr Cross----Pxr Cross shader

Pxr DebugShadingContext----Pxr DebugShadingContext shader

Pxr Default----Pxr Default integrator shader

Pxr Direct Lighting----Pxr Direct Lighting integrator shader

Pxr Dirt----Pxr Dirt shader

Pxr Disk Light----Pxr Disk Light shader

Pxr Disney----Pxr Disney bxdf shader

Pxr Disp Transform----Pxr Disp Transform shader

Pxr Disp Vector Layer----Pxr Disp Vector Layer shader

Pxr Displace----Pxr Displace shader

Pxr Displacement----Pxr Displacement shader

Pxr Display Filter Combiner----Pxr Display Filter Combiner shader

Pxr Disps Calar Layer----Pxr Disps Calar Layer shader

Pxr Distant Light----Pxr Distant Light shader

Pxr Dome Light----Pxr Dome Light shader

Pxr Dot----Pxr Dot shader

Pxr Envday Light----Pxr Envday Light shader

Pxr Exposure----Pxr Exposure shader

Pxr FacingRatio----Pxr FacingRatio shader

Pxr Filmic Tone Mapper Display Filter----Pxr Filmic Tone Mapper Display Filter shader

Pxr Filmic Tone Mapper Sample Filter----Pxr Filmic Tone Mapper Sample Filter shader

Pxr Flakes----Pxr Flakes shader

Pxr Fractal----Pxr Fractal pattern shader

Pxr Fractialize----Pxr Fractialize shader

Pxr Gamma----Pxr Gamma shader

Pxr Geometric AOVs----Pxr Geometric AOVs shader

Pxr Gobo----Pxr Gobo light filter shader

Pxr Gobolight Filter----Pxr Gobolight Filter shader

Pxr Grade Display Filter----Pxr Grade Display Filter shader

Pxr Grade Sample Filter----Pxr Grade Sample Filter shader

Pxr Hair Color----Pxr Hair Color shader.

Pxr Half Buffer Error Filter----Pxr Half Buffer Error Filter shader.

Pxr Hsl----Pxr Hsl shader

Pxr Image Display Filter----Pxr Image Display Filter shader

Pxr Image Plane Filter----Pxr Image Plane Filter shader

Pxr Int Mult Light Filter----Pxr Int Mult Light Filter shader

Pxr Invert----Pxr Invert shader

Pxr Layer----Pxr Layer shader

Pxr Layer Mixer----Pxr Layer Mixer shader

Pxr Layered Texture----Pxr Layered Texture shader

Pxr Layeredblend----Pxr Layeredblend shader

Pxr Light Probe----Pxr Light Probe shader

Pxr Lightemission----Pxr Lightemission shader

Pxr Lmdiffuse----Pxr Lmdiffuse shader

Pxr Lmglass----Pxr Lmglass shader

Pxr Lmlayer----Pxr Lmlayer shader

Pxr Lmmixer----Pxr Lmmixer shader

Pxr Lmplastic----Pxr Lmplastic shader

Pxr Lmsubsurface----Pxr Lmsubsurface shader

Pxr Manifold 3D----Pxr Manifold 3D manifold shader

Pxr Manifold2d----Pxr Manifold2d shader

Pxr Manifold3dn----Pxr Manifold3dn shader

Pxr Marschnerhair----Pxr Marschnerhair shader

Pxr Matteid----Pxr Matteid shader

Pxr Mesh Light----Pxr Mesh Light shader

Pxr Mix----Pxr Mix shader

Pxr Multi Texture----Pxr Multi Texture shader

Pxr Normalmap----Pxr Normalmap shader

Pxr Occlusion----Pxr Occlusion shader

Pxr Omini Directional Stereo----Pxr Omini Directional Stereo

Pxr Osl----Pxr Osl shader

Pxr Path Tracer----Pxr Path Tracer integrator shader

Pxr Portal Light----Pxr Portal Light shader

Pxr Primvar----Pxr Primvar shader

Pxr Projection Stack----Pxr Projection Stack shader

Pxr Projectionlayer----Pxr Projectionlayer shader

Pxr Projector----Pxr Projector shader

Pxr Ptexture----Pxr Ptexture shader

Pxr Ramp----Pxr Ramp shader

Pxr Ramp Light Filter----Pxr Ramp Light Filter shader

Pxr Random Texture Manifold----Pxr Random Texture Manifold shader.

Pxr Rect Light----Pxr Rect Light shader

Pxr Remap----Pxr Remap shader

Pxr Rod Light Filter----Pxr Rod Light Filter shader

Pxr Rolling Shutter----Pxr Rolling Shutter shader

Pxr Roundcube----Pxr Roundcube shader

Pxr Sample Filter Combiner----Pxr Sample Filter Combiner shader

Pxr Seexpr----Pxr Seexpr shader

Pxr Shaded Side----Pxr Shaded Side shader

Pxr Shadow Display Filter----Pxr Shadow Display Filter shader

Pxr Shadow Filter----Pxr Shadow Filter shader

Pxr Sphere Light----Pxr Sphere Light shader

Pxr Std Env Day Light----Pxr Std Env Day Light light shader

Pxr Std Env Map Light----Pxr Std Env Map Light light shader

Pxr Surface----Pxr Surface shader

Pxr Tangentfield----Pxr Tangentfield shader

Pxr Tee----Pxr Tee shader

Pxr Texture----Pxr Texture shader

Pxr Thinfilm----Pxr Thinfilm shader

Pxr Threshold----Pxr Threshold shader

Pxr Tile Manifold----Pxr Tile Manifold shader

Pxr Tofloat----Pxr Tofloat shader

Pxr Tofloat3----Pxr Tofloat3 shader

Pxr UPBP----Pxr UPBP shader

Pxr VCM----Pxr VCM integrator shader

Pxr Validatebxdf----Pxr Validatebxdf shader

Pxr Variable----Pxr Variable shader

Pxr Vary----Pxr Vary shader

Pxr Visualizer----Pxr Visualizer shader

Pxr Volume----Pxr Volume shader

Pxr Voronoise----Pxr Voronoise pattern shader

Pxr White Point Display Filter----Pxr White Point Display Filter shader

Pxr White Point Sample Filter----Pxr White Point Sample Filter shader

Pxr Worley----Pxr Worley shader

PxrLm Metal----PxrLm Metal shader

Pyro Blackbody----Converts a temperature value into color (chroma) and intensity according to the blackbody radiation model.

Pyro Color Correct----Provides color correction functions.

Pyro Color Model----Provides constant, artistic, and physically correct (blackbody) tint as well as color correction functions.

Pyro Color Volume----Provides functions for editing color fields by conditioning the field values, adding noise, filtering, and color correction.

Pyro Density Volume----Provides functions for editing fields such as density by conditioning the field values, adding noise, and filtering.

Pyro Displace

Pyro Field

Pyro Noise

Pyro Shader----Flexible, production-quality fire and smoke shader.

Pyro Shader Core----Provides the core functionality needed to build a high-quality volumetric shader.

Quaternion----Takes an angle and an axis and constructs the quaternion representing the rotation about that axis.

Quaternion Distance----Computes distance between quaternions in radians.

Quaternion Invert----Takes an quaternion inverts it..

Quaternion Multiply----Performs a quaternion multiplication with its two inputs.

Quaternion to Angle/Axis----Converts a quaternion to angle/axis form.

Quaternion to Matrix3----Converts a vector4, representing a quaternion, to a matrix3 value, representing the same rotation.

RGB to HSV----Converts RGB color space to HSV color space.

RSL Gather Loop----Sends rays into the scene and contains a subnetwork of VOPs to operate on the information gathered from the shaders of surfaces hit by the rays.

RSL Material----Implements an RSL material.

Radians to Degrees----Converts radians to degrees.

Rainbow----Generates a non-repeating rainbow color ramp by modulating the hue over the range of the parametric coordinate s and using the given saturation and value to compute the HSV color.

Ramp Filter----Adds anti-aliased analytical filtering to the output of a Ramp Parameter VOP.

Ramp Parameter----Represents a user-editable ramp parameter.

Ramps----Generates repeating filtered ramps.

Random----Generates a random number based on the position in one, three, or four dimensions.

Random Sobol----Generates a random number in a Sobol sequence.

Random Value

Ray Bounce Level----Returns the current ray-bounce level.

Ray Bounce Weight----Returns the amount that the current bounce level will contribute to the final pixel color.

Ray Hit----This operator sends a ray from the position P along the direction specified by the direction D, and returns the distance to the object intersected or a negative number if not object found.

Ray Trace----Sends a ray starting at origin P and in the direction specified by the normalized vector D.

Reflect----Returns the vector representing the reflection of the direction against the normal vector.

Reflected Light----Computes the amount of reflected light which hits the surface.

Refract----Computes the refraction ray given an incoming direction, the normalized normal and an index of refraction.

Refracted Light----Sends a ray starting at origin P and in the direction specified by the normalized vector I.

Regex Find----Finds the given regular expression in the string.

Regex Findall----Finds all instances of the given regular expression in the string.

Regex Match----Result 1 if the entire input string matches the expression.

Regex Replace----Replaces instances of find_regex with replace_regex.

Regex Split----Splits the given string based on regex match.

Relative to Bounding Box----Returns the relative position of the point given with respect to the bounding box of the specified geometry.

Relative to Point Bounding Box----Returns the relative position of the point given with respect to the bounding box of the specified geometry.

Remove Index----Removes an item at the given index from an array.

Remove Point----Removes points from the geometry.

Remove Primitive

Remove Value----Removes an item from an array.

Render State----Gets state information from the renderer.

RenderMan Bias

RenderMan Calculate Normal

RenderMan Deriv

RenderMan Du/Dv

RenderMan Environment Map

RenderMan Gain

RenderMan Illuminance Loop

RenderMan Illuminate Construct

RenderMan Import Value

RenderMan Indirect Diffuse

RenderMan Logarithm

RenderMan Occlusion

RenderMan Ray Information

RenderMan Render State Information

RenderMan Shadow Map

RenderMan Step

RenderMan Surface Color

RenderMan Texture Map

RenderMan Texture Map Information

RenderMan Transform

RenderMan Transform Color

RenderMan Z-Depth From Camera

Reorder----Reorders items in an array or string.

Report Error----Optionally report a custom VEX error or warning.

Reshape Value----Modulates input value using a variety of methods.

Resolution----Returns the pixel resolution of an input.

Rest Position----Checks if the geometry attribute "rest" is bound and, if so, uses it as the rest position for shading.

Return----Generates a return statement inside a method or a function defined by the parent subnet.

Reverse----Adds an item to an array or string.

Rings----Generates repeating filtered rings.

Ripples----Generates repeating ripples.

Rotate----Applies a rotation by 'angle' radians to the given 3×3 or 4×4 matrix.

Rotate by Quaternion----Rotates a vector by a quaternion.

Round to Integer----Rounds the argument to the closest integer.

Rounded Edge----Blends the normals between faces within specified radius.

Rounded Hexes----Generates repeating filtered rounded hexagons.

Rounded Stars----Generates repeating filtered rounded five-pointed stars.

Run External Program Procedural----This procedural will run an external application in order to generate geometry at render time.

SSS Component----Adds energy conservation functionality and additional controls to the Physical SSS VOP.

Sample Sphere----Samples the interior or surface of the unit circle, sphere, or hypersphere, within a max angle of a direction.

Scale----Scales a 3×3 or 4×4 matrix by 'amount' units along the x,y, and z axes.

Scales----Generates a scale-like pattern and returns the displaced position, normal, and displacement amount.

Sensor Panorama Color----Requests the rendered color from a specified direction

Sensor Panorama Cone----Returns an average direction, color, depth, and strength.

Sensor Panorama Create----Renders the surrounding environment

Sensor Panorama Depth----Requests the rendered depth from a specified direction

Sensor Panorama Save----Saves the rendered panorama to a specified output file

Sensor Save----Saves sensor data to image files.

Set Agent Clip Names----Sets the current animation clips for an agent primitive.

Set Agent Clip Times----Sets the current times for an agent primitive’s animation clips.

Set Agent Clip Weights----Sets the blend weights for an agent primitive’s animation clips.

Set Agent Layer----Sets the current layer or collision layer of an agent primitive.

Set Agent Transforms----Overrides the transforms of an agent primitive.

Set Attribute

Set CHOP Attribute----Sets a CHOP attribute value.

Set Channel Tranform----Sets a transform value when evaluating a Channel VOP in Tranlate/Rotate/Scale mode.

Set Channel Value----Sets a channel value when evaluating a Channel VOP in Channel/Sample modes.

Set Element----Sets the element at the specified index.

Set Layer Export----Adds layer exports to the Shader Layer struct

Set Matrix Component----Assigns a value to one of the matrix’s components.

Set Matrix2 Component----Assigns a value to one of the matrix2's components.

Set Matrix3 Component----Assigns a value to one of the matrix3's components.

Set Primitive Vertex

Set Vector Component----Assigns a value to one of the vector’s components.

Set Vector2 Component----Assigns a value to one of the vector2's components.

Set Vector4 Component----Assigns a value to one of the vector4's components.

Shader Output Export Variables----Represents export parameters in a shader call.

Shader Output Global Variables----Represents global variables that are bound as output parameters in a shader call.

Shading Area----Computes the shading area of the given variable.

Shading Derivative----Computes the derivative of a given variable with respect to the s or t parametric coordinate.

Shading Layer Parameter----Creates a parameter to appear in the signature of the VEX function defined by the VOP network (VOPNET).

Shading Normal----Computes the normal at the location specified by the P position.

Shadow----This shader calls the shadow shader inside an illuminance loop.

Shadow Map----Shadow Map treats the depth map as if the image were rendered from a light source.

Shadow Matte----Implements a shadowmatte shader that occludes geometry behind the surface being rendered.

Sign----Returns -1 if the input is less than 0, otherwise it returns 1.

Sine----Performs a sine function.

Skin Shader Core----A skin shader with three levels of subsurface scattering.

Slice----Slices a sub-string or sub-array of a string or array.

Smooth----Computes a number between zero and one.

Smooth Rotation----Returns the closest equivalent Euler rotations to a reference rotation.

Snippet----Runs a VEX snippet to modify the incoming values.

Soft Clip----Increases or decreases contrast for values at the top of the input range.

Soft Dots----Generates repeating soft dots.

Sort----Returns the array sorted in increasing order.

Specular----Generates a color using the selected specular lighting model calculation.

Specular Sheen----Generates a color using a specular lighting model with a Fresnel falloff calculation.

Spherical Linear Interp----Computes a spherical linear interpolation between its two quaternion inputs, and outputs the intermediate quaternion.

Splatter----Generates a splatter pattern and returns the splatter amount.

Spline----Computes either a Catmull-Rom (Cardinal) spline or a Linear spline between the specified key points, given an interpolant (u) in the domain of the spline.

Split String----Splits a string into tokens.

Sprites Procedural----This procedural will render points as sprites.

Square Root----Computes the square root of the argument.

Starts With----Result 1 if the string starts with the specified string.

String Length----Returns the length of the string.

String to Character----Converts an UTF8 string into a codepoint.

Strip----Strips leading and trailing whitespace from a string.

Stripes----Generates repeating filtered stripes.

Struct----Creates, modifies, or de-structures an instance of a structured datatype.

Struct Pack----Bundles input values into an instance of an ad-hoc struct.

Struct Unpack----Extracts one or more values from a struct by member name.

Sub Network----Contains other VOP operators.

Subnet Connector----Represents an input or an output (or both) of the parent VOP subnet.

Subnet Input----Allows the connection of operators outside a subnet to operators inside the subnet.

Subnet Output----Allows the connection of operators inside a subnet to operators outside the subnet.

Subtract---Outputs the result of subtracting all its inputs.

Subtract Constant----Subtracts the specified constant value from the incoming integer, float, vector or vector4 value.

Surface Color----Generates a basic color with a choice of tinting with the point color and/or a color map.

Surface Distance----Finds the shortest distance between a point and a source point group.

Switch----Switches between network branches based on the value of an input.

Switch Lighting BSDF----Use a different bsdf for direct or indirect lighting.

Swizzle Vector----Rearranges components of a vector.

Swizzle Vector2----Rearranges components of a vector2.

Swizzle Vector4----Rearranges components of a vector4.

Tangent----Performs a tangent function.

Tangent Normal----Transform an input normal to UV/tangent space

Tangent Normal Remap----Transform an input normal from UV/tangent to current space

Tangent Normals----Exports shader normals as a render plane.

Tetrahedron Adjacent----Returns primitive number of an adjacent tetrahedron.

Tetrahedron Adjacent----Returns vertex indices of each face of a tetrahedron.

Texture----Computes a filtered sample of the texture map specified and returns an RGB or RGBA color.

Texture 3D----Returns the value of a 3D image at a specified position within that image.

Texture 3D Box----Queries the 3D texture map specified and returns the bounding box information for the given channel in the min and max corner vectors.

Texture Map

Thin Film Fresnel----Computes the thin film reflection and refraction contributions given a normalized incident ray, a normalized surface normal, and an index of refraction.

Tiled Boxes----Generates staggered rectangular tiles.

Tiled Hexagons----Generates staggered hexagonal tiles.

Timing----Returns the frame range and rate of the given input.

Title Case----Returns a string that is the titlecase version of the input string.

To Lower----Returns a string that is the lower case version of the input string.

To NDC----Transforms a position into normal device coordinates.

To NDC

To Polar----Converts cartesian coordinates to polar coordinates.

To Upper----Returns a string that is the upper case version of the input string.

Trace----Uses the vex gather function to send a ray and return with the reflected or refracted colors.

Transform----Transforms a vector to or from an object’s transform space, or one of several other spaces, such as world or camera space.

Transform Matrix

Translate----Translates a 4×4 matrix 'amount' units along the x,y,z and possibly w axes.

Transpose

Trigonometric Functions----Performs a variety of trigonometric functions.

Turbulent Noise----Can compute three types of 1D and 3D noise with the ability to compute turbulence with roughness and attenuation.

Two Sided----Generates a two sided surface.

Two Way Switch----Takes an integer input.

USD Global Variables----Provides outputs representing commonly used input variables for processing USD primitive attributes inside an Attribute VOP LOP.

USD Preview Surface----USD Preview Surface shader

USD Prim Var Reader----USD Prim Var Reader shader

USD UV Texture----USD UV Texture shader

UV Coords----Returns texture coordinates or geometric s and t, depending on what is defined.

UV Noise----Disturbs the incoming parametric s and t coordinates using anti aliased noise generated from the Surface Position input.

UV Planar Project----Computes UV co-ordinates projected along a single axis, derived from the position of an object, and generates a mask relative to the projection axis.

UV Position

UV Project----Assigns texture coordinates based on the specified projection type.

UV Transform----Transforms texture coordinates by the inverse of the matrix consisting of the translation, rotation, and scale amounts.

UV Tri-planar Project----Projects texture maps along X, Y, and Z axes and blends them together at the seams.

Unified Noise----Presents a unified interface and uniform output range for all the noise types available in VEX.

Unified Noise----Presents a unified interface and uniform output range for all the noise types available in VEX.

Unified Noise Static----Presents a unified interface and uniform output range for all the noise types available in VEX.

Unique Value Count of Attribute

Unique Values of Attribute

VOP Force Global----Provides outputs that represent all the global variables for the Force VOP network type.

VOP Force Output Variables----Simple output variable for VOP Force Networks.

Vector Cast----Converts between different vector types.

Vector To Float----Unpacks a vector into its three components.

Vector To Quaternion----Takes an angle/axis vector and constructs the quaternion representing the rotation about that axis.

Vector To Vector4---Converts a vector to a vector4.

Vector to Matrix3----Converts rows values to a 3×3 matrix value.

Vector to Vector2----Converts a vector to a vector2 and also returns the third component of the vector.

Vector2 To Float----Unpacks a vector2 into its two components.

Vector2 To Vector----Converts a vector2 to a vector.

Vector2 To Vector4----Converts a pair of vector2s into a vector4.

Vector2 to Matrix2----Converts rows values to a 2×2 matrix value.

Vector4 to Float----Unpacks a vector4 into its four components.

Vector4 to Matrix----Converts rows values to a 4×4 matrix value.

Vector4 to Vector----Converts a vector4 to a vector and also returns the fourth component of the vector4.

Vector4 to Vector2----Converts a vector4 to a pair of vector2s..

Veins----Generates an anti-aliased vein pattern that can be used in any VEX context.

Vex Volume Procedural----This procedural will generate a volume from a CVEX shader.

Visualize----Exports a vis_ prefixed attribute.

Volume Density to Opacity----Computes the opacity of a uniform volume given a density.

Volume Gradient----Calculates the gradient of a volume primitive stored in a disk file.

Volume Index----Gets the value of a voxel from a volume primitive stored in a disk file.

Volume Index To Pos----Calculates the position of a voxel in a volume primitive stored in a disk file.

Volume Index Vector----Gets the vector value of a voxel from a volume primitive stored in a disk file.

Volume Model----A shading model for volume rendering.

Volume Pos To Index----Calculates the voxel closest to a voxel of a volume primitive stored in a disk file.

Volume Resolution----Gets the resolution of a volume primitive stored in a disk file.

Volume Sample----Samples the value of a volume primitive stored in a disk file.

Volume Sample Vector----Samples the vector value of a volume primitive stored in a disk file.

Volume VOP Global Parameters----Provides outputs that represent all the global variables for the Volume VOP network type.

Volume VOP Output Variables----Simple output variable for Volume VOP Networks.

Voronoi Noise----Computes 1D, 3D, and 4D Voronoi noise, which is similar to Worley noise but has additional control over jittering.

Wave Vector----Computes the wave vector for a given index in a grid of specified size.

Waves----Simulates rolling waves with choppiness of various frequencies, and outputs the positional and normal displacements as well as the amount of displacement.

Wire Pattern----Returns float between 0 and 1 which defines a wire grid pattern useful for simulating screens or visualizing parametric or texture coordinates.

Worley Noise----Computes 1D, 3D, and 4D Worley noise, which is synonymous with "cell noise".

XYZ Distance----Finds closest position on a primitive in a given geometry file.

Xor----Performs a logical "xor" operation between its inputs.

agentaddclip----Add a clip into an agent’s definition.

argsort----Returns the indices of a sorted version of an array.





=================================================================
