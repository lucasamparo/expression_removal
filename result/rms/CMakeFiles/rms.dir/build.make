# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.5

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/lucasamparo/expression-removal/result/rms

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/lucasamparo/expression-removal/result/rms

# Include any dependencies generated for this target.
include CMakeFiles/rms.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/rms.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/rms.dir/flags.make

CMakeFiles/rms.dir/rms.cpp.o: CMakeFiles/rms.dir/flags.make
CMakeFiles/rms.dir/rms.cpp.o: rms.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/lucasamparo/expression-removal/result/rms/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/rms.dir/rms.cpp.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/rms.dir/rms.cpp.o -c /home/lucasamparo/expression-removal/result/rms/rms.cpp

CMakeFiles/rms.dir/rms.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/rms.dir/rms.cpp.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/lucasamparo/expression-removal/result/rms/rms.cpp > CMakeFiles/rms.dir/rms.cpp.i

CMakeFiles/rms.dir/rms.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/rms.dir/rms.cpp.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/lucasamparo/expression-removal/result/rms/rms.cpp -o CMakeFiles/rms.dir/rms.cpp.s

CMakeFiles/rms.dir/rms.cpp.o.requires:

.PHONY : CMakeFiles/rms.dir/rms.cpp.o.requires

CMakeFiles/rms.dir/rms.cpp.o.provides: CMakeFiles/rms.dir/rms.cpp.o.requires
	$(MAKE) -f CMakeFiles/rms.dir/build.make CMakeFiles/rms.dir/rms.cpp.o.provides.build
.PHONY : CMakeFiles/rms.dir/rms.cpp.o.provides

CMakeFiles/rms.dir/rms.cpp.o.provides.build: CMakeFiles/rms.dir/rms.cpp.o


# Object files for target rms
rms_OBJECTS = \
"CMakeFiles/rms.dir/rms.cpp.o"

# External object files for target rms
rms_EXTERNAL_OBJECTS =

rms: CMakeFiles/rms.dir/rms.cpp.o
rms: CMakeFiles/rms.dir/build.make
rms: /usr/local/lib/libopencv_dnn.so.3.3.0
rms: /usr/local/lib/libopencv_ml.so.3.3.0
rms: /usr/local/lib/libopencv_objdetect.so.3.3.0
rms: /usr/local/lib/libopencv_shape.so.3.3.0
rms: /usr/local/lib/libopencv_stitching.so.3.3.0
rms: /usr/local/lib/libopencv_superres.so.3.3.0
rms: /usr/local/lib/libopencv_videostab.so.3.3.0
rms: /usr/local/lib/libopencv_calib3d.so.3.3.0
rms: /usr/local/lib/libopencv_features2d.so.3.3.0
rms: /usr/local/lib/libopencv_flann.so.3.3.0
rms: /usr/local/lib/libopencv_highgui.so.3.3.0
rms: /usr/local/lib/libopencv_photo.so.3.3.0
rms: /usr/local/lib/libopencv_video.so.3.3.0
rms: /usr/local/lib/libopencv_videoio.so.3.3.0
rms: /usr/local/lib/libopencv_imgcodecs.so.3.3.0
rms: /usr/local/lib/libopencv_imgproc.so.3.3.0
rms: /usr/local/lib/libopencv_core.so.3.3.0
rms: CMakeFiles/rms.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/lucasamparo/expression-removal/result/rms/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable rms"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/rms.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/rms.dir/build: rms

.PHONY : CMakeFiles/rms.dir/build

CMakeFiles/rms.dir/requires: CMakeFiles/rms.dir/rms.cpp.o.requires

.PHONY : CMakeFiles/rms.dir/requires

CMakeFiles/rms.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/rms.dir/cmake_clean.cmake
.PHONY : CMakeFiles/rms.dir/clean

CMakeFiles/rms.dir/depend:
	cd /home/lucasamparo/expression-removal/result/rms && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/lucasamparo/expression-removal/result/rms /home/lucasamparo/expression-removal/result/rms /home/lucasamparo/expression-removal/result/rms /home/lucasamparo/expression-removal/result/rms /home/lucasamparo/expression-removal/result/rms/CMakeFiles/rms.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/rms.dir/depend

