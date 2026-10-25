"""Single discreet open-source licenses page (/licenses). Keeps the MIT/GPLv3 notices required by upstream."""
no_cache = 1
sitemap = 0


def get_context(context):
	context.no_breadcrumbs = True
	context.components = [
		{
			"name": "Frappe Framework",
			"license": "MIT",
			"copyright": "Copyright (c) 2016-present Frappe Technologies Pvt. Ltd. <developers@frappe.io>",
			"note": "Permission is hereby granted, free of charge, to any person obtaining a copy of this software, subject to the conditions of the MIT License. "
			"THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND.",
			"source": "https://github.com/frappe/frappe",
			"license_url": "https://github.com/frappe/frappe/blob/develop/LICENSE",
		},
		{
			"name": "ERPNext",
			"license": "GNU GPL v3",
			"copyright": "Copyright (c) Frappe Technologies Pvt. Ltd. and Contributors",
			"note": "This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3. "
			"It is distributed WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.",
			"source": "https://github.com/frappe/erpnext",
			"license_url": "https://www.gnu.org/licenses/gpl-3.0.html",
		},
		{
			"name": "Frappe HR (HRMS)",
			"license": "GNU GPL v3",
			"copyright": "Copyright (c) Frappe Technologies Pvt. Ltd. and Contributors",
			"note": "Distributed under the GNU General Public License v3 WITHOUT ANY WARRANTY.",
			"source": "https://github.com/frappe/hrms",
			"license_url": "https://www.gnu.org/licenses/gpl-3.0.html",
		},
		{
			"name": "Fonts: Urbanist, Inter, Noto Sans Arabic, DM Mono, Instrument Serif",
			"license": "SIL Open Font License 1.1",
			"copyright": "Copyright the Urbanist, Inter, Noto, DM Mono and Instrument Serif project authors",
			"note": "Bundled web fonts are used under the SIL Open Font License, Version 1.1.",
			"source": "https://fonts.google.com",
			"license_url": "https://openfontlicense.org",
		},
	]
	return context
