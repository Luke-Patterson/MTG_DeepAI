import line_profiler
import builtins
import sys
import os
prof = line_profiler.LineProfiler()
builtins.__dict__['profile'] = prof
exec_ = getattr(builtins, "exec")
def execfile(filename, globals=None, locals=None):
        with open(filename, 'rb') as f:
            exec_(compile(f.read(), filename, 'exec'), globals, locals)

script_file = 'rand_data.py'
__file__ = script_file
__name__ = '__main__'
# Make sure the script's directory is on sys.path instead of just
# kernprof.py's.
sys.path.insert(0, os.path.dirname(script_file))
execfile_ = execfile
ns = locals()
execfile(script_file, ns, ns)
prof.dump_stats('logs/rand_data_line_profiler.txt')
prof.print_stats()
