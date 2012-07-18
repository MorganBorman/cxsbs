import sys
import os
import time

sys.path.append(os.path.abspath("pydeps"))

import pyTensible

pyTensible.setup_logging(os.path.abspath('plugin_loader.log'))

plugin_loader = pyTensible.PluginLoader()

__builtins__.instance_root = os.path.abspath("instances/dev")

plugin_loader.load_plugins(os.path.abspath('plugins'))

import org

org.cxsbs.core.server.instance.run()

try:
    time.sleep(1000000)
except KeyboardInterrupt:
    org.cxsbs.core.events.manager.trigger_event("server_stop")