frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["KodeERP Sales Trend"] = {
	method: "kodenova_theme.api.dashboard.sales_trend",
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
