import sys
from mate.vm.universe import main, Exit

try:
    main(sys.argv)
except Exit, e:
    sys.exit(e.code)
sys.exit(0)
