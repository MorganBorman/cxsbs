echo "Running make clean..."
if [ -e "Makefile" ]
then
  make clean >/dev/null 2>/dev/null
fi
echo "Removing bin/ directory..."
rm -r src/bin >/dev/null 2>/dev/null
rm -r bin >/dev/null 2>/dev/null
echo "Removing cmake files..."
rm CMakeCache.txt >/dev/null 2>/dev/null
find . -name "Makefile" -exec rm -r '{}' ';' >/dev/null 2>/dev/null
find . -name "CMakeFiles" -exec rm -r '{}' ';' >/dev/null 2>/dev/null
find . -name "cmake_install.cmake" -exec rm '{}' ';' >/dev/null 2>/dev/null
echo "Removing .pyc files..."
find . -name "*.pyc" -exec rm '{}' ';' >/dev/null 2>/dev/null
echo "Done."
