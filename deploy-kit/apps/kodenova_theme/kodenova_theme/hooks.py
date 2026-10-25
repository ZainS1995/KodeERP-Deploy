app_name = "kodenova_theme"
app_title = "Intelliconz Accounting Brand"
app_publisher = "Kodenova"
app_description = "Kodenova brand theme and UX layer for Intelliconz Accounting (ERPNext v16)"
app_email = "dev@example.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "kodenova_theme",
# 		"logo": "/assets/kodenova_theme/logo.png",
# 		"title": "Kodenova Theme",
# 		"route": "/kodenova_theme",
# 		"has_permission": "kodenova_theme.api.permission.has_app_permission",
# 	}
# ]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `kodenova_theme/dock/kodenova_theme/kodenova_theme.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = ["/assets/kodenova_theme/css/kodenova_theme.css?v=9", "/assets/kodenova_theme/css/kodenova_motion.css?v=9", "/assets/kodenova_theme/css/kodeerp_dashboard.css?v=9", "/assets/kodenova_theme/css/kodeerp_v5.css?v=9"]
app_logo_url = "/assets/kodenova_theme/images/kodeerp-icon-192.png"
app_include_js = ["/assets/kodenova_theme/js/kodenova_theme.js?v=9", "/assets/kodenova_theme/js/kodeerp_list_cards.js?v=9", "/assets/kodenova_theme/js/kodeerp_tabs.js?v=9", "/assets/kodenova_theme/js/kodeerp_line_dims.js?v=9"]

# include js, css files in header of web template
web_include_css = ["/assets/kodenova_theme/css/kodenova_theme.css?v=9", "/assets/kodenova_theme/css/kodenova_motion.css?v=9", "/assets/kodenova_theme/css/kodenova_login.css?v=9", "/assets/kodenova_theme/css/kodeerp_v5.css?v=9"]

# Brand the outgoing email container (premailer inlines it) — supported hook, appended after frappe's email.bundle.css
email_css = ["/assets/kodenova_theme/css/kodenova_email.css"]

# Relabel apps-screen tiles / rail logo with KodeERP equivalents (boot payload only)
extend_bootinfo = "kodenova_theme.boot.extend_bootinfo"
web_include_js = ["/assets/kodenova_theme/js/kodenova_web.js?v=9", "/assets/kodenova_theme/js/kodenova_login.js?v=9"]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "kodenova_theme/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "kodenova_theme/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "kodenova_theme.utils.jinja_methods",
# 	"filters": "kodenova_theme.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "kodenova_theme.install.before_install"
# after_install = "kodenova_theme.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "kodenova_theme.uninstall.before_uninstall"
# after_uninstall = "kodenova_theme.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "kodenova_theme.utils.before_app_install"
# after_app_install = "kodenova_theme.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "kodenova_theme.utils.before_app_uninstall"
# after_app_uninstall = "kodenova_theme.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "kodenova_theme.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "kodenova_theme.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "kodenova_theme.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["kodenova_theme.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"kodenova_theme.tasks.all"
# 	],
# 	"daily": [
# 		"kodenova_theme.tasks.daily"
# 	],
# 	"hourly": [
# 		"kodenova_theme.tasks.hourly"
# 	],
# 	"weekly": [
# 		"kodenova_theme.tasks.weekly"
# 	],
# 	"monthly": [
# 		"kodenova_theme.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "kodenova_theme.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "kodenova_theme.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "kodenova_theme.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "kodenova_theme.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["kodenova_theme.utils.before_request"]
# after_request = ["kodenova_theme.utils.after_request"]

# Job Events
# ----------
# before_job = ["kodenova_theme.utils.before_job"]
# after_job = ["kodenova_theme.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"kodenova_theme.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []



# ---- KodeERP branding (supported hooks only) ----
after_install = "kodenova_theme.branding.after_install"
after_migrate = [
	"kodenova_theme.branding.after_migrate",
	"kodenova_theme.dashboards.apply_default_workspace",
]
website_context = {
	"favicon": "/assets/kodenova_theme/images/kodeerp-favicon.ico",
	"splash_image": "/assets/kodenova_theme/images/kodeerp-icon-512.png",
}


# ---- v0.5 white-label ----
# Retire upstream-branded public routes; /attribution is replaced by the single /licenses page.
website_redirects = [
	{"source": "/attribution", "target": "/licenses"},
	{"source": "/payment_setup_certification", "target": "/"},
	{"source": r"/hrms(/.*)?", "target": "/desk"},
	# ERPNext's separate Vue banking app is unthemed; route demo users to the themed desk tool instead.
	{"source": r"/banking(/.*)?", "target": "/desk/bank-reconciliation-tool"},
]

# Privacy: non-admin users can only see their own User record.
permission_query_conditions = {"User": "kodenova_theme.permissions.user_query"}
has_permission = {"User": "kodenova_theme.permissions.user_has_permission"}

# New desk users land on the KodeERP Home workspace.
doc_events = {
	"User": {"after_insert": "kodenova_theme.dashboards.set_default_workspace_for_new_user"},
}
# Item/tax lines follow the header cost centre + accounting dimensions (toggle: site_config kodeerp_sync_line_dimensions)
for _dt in ("Sales Invoice", "Purchase Invoice", "POS Invoice", "Sales Order", "Delivery Note", "Purchase Order", "Purchase Receipt"):
	doc_events[_dt] = {
		"before_validate": "kodenova_theme.accounting.line_dimensions.sync_line_dimensions",
		"validate": "kodenova_theme.accounting.line_dimensions.sync_line_dimensions",
	}
