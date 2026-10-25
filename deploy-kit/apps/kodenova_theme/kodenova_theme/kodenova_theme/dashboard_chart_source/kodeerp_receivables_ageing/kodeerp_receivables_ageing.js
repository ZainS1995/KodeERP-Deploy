frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["KodeERP Receivables Ageing"] = {
	method: "kodenova_theme.api.dashboard.receivables_ageing",
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
