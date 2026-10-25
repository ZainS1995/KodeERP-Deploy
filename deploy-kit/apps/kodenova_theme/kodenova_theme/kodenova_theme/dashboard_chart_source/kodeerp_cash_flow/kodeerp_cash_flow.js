frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["KodeERP Cash Flow"] = {
	method: "kodenova_theme.api.dashboard.cash_flow",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
	],
};
