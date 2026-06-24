# -*- coding: utf-8 -*-
import sys
sys.path.append('.')
import std_misrac, std_misracpp, std_certc, std_certcpp, std_autosar

sys.stdout.reconfigure(encoding='utf-8')

print("MISRA C:", len(std_misrac.RULES))
print("MISRA C++:", len(std_misracpp.RULES))
print("CERT C:", len(std_certc.RULES))
print("CERT C++:", len(std_certcpp.RULES))
print("AUTOSAR C++14:", len(std_autosar.RULES))
