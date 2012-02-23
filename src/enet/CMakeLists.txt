project(enet)

set(enet_srcs
	callbacks.c
	compress.c
	host.c
	list.c
	packet.c
	peer.c
	protocol.c
	unix.c
	win32.c)
	
add_definitions(-DHAS_SOCKLEN_T)

include_directories(include)

add_library(enet STATIC ${enet_srcs})
