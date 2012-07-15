subdirs(enet shared)

#set(CMAKE_USE_PYTHON_VERSION "2.7")

find_package(PythonLibs REQUIRED)
find_package(ZLIB REQUIRED)
find_package(Threads REQUIRED)

set(cxsbs_srcs
	engine/server.cpp
	engine/command.cpp

	fpsgame/server.cpp
	
	stats/stats.cpp
	stats/pk_dealer.cpp

	pycontrol/sbpy.cpp
	pycontrol/servermodule.cpp)

set(CXSBS_LIBS
	enet
	sauertools
	${PYTHON_LIBRARIES}
	${ZLIB_LIBRARIES}
	${CMAKE_THREAD_LIBS_INIT}
	-lutil
	-ldl)
    
IF(WIN32)
set(CXSBS_LIBS ${CXSBS_LIBS} ws2_32 winmm)
ENDIF(WIN32)

include(CheckFunctionExists)
include(CheckSymbolExists)

set(CMAKE_CXX_FLAGS "-rdynamic -Wall -g -pg")

check_function_exists(gethostbyaddr_r, HAS_GETHOSTBYADDR_R)
check_function_exists(gethostbyname_r, HAS_GETHOSTBYNAME_R)
check_function_exists(poll, HAS_POLL)
check_function_exists(fcntl, HAS_FCNTL)
check_function_exists(inet_pton, HAS_INET_PTON)
check_function_exists(inet_ntop, HAS_INET_NTOP)

check_symbol_exists("struct msghdr.msg_flags" "sys/socket.h" HAS_MSGHDR_FLAGS)
check_symbol_exists("socklen_t" "sys/types.h;sys/socket.h" HAS_SOCKLEN_T)

add_definitions(-DSTANDALONE)

include_directories(${CMAKE_SOURCE_DIR}/src/engine
	${CMAKE_SOURCE_DIR}/src/fpsgame
	${CMAKE_SOURCE_DIR}/src/shared
	${CMAKE_SOURCE_DIR}/src/tools
	${CMAKE_SOURCE_DIR}/src/stats
	${CMAKE_SOURCE_DIR}/src/pycontrol
	${CMAKE_SOURCE_DIR}/src/enet/include
	${PYTHON_INCLUDE_PATH}
	${ZLIB_INCLUDE_PATH})

add_executable(../bin/cxsbs ${cxsbs_srcs})
target_link_libraries(../bin/cxsbs ${CXSBS_LIBS})

install(TARGETS ../bin/cxsbs DESTINATION bin)

