# KodeERP: reuse the upstream printview context; only the template (printview.html) is overridden.
from frappe.www.printview import *  # noqa: F401,F403
from frappe.www.printview import get_context  # noqa: F401

no_cache = 1
