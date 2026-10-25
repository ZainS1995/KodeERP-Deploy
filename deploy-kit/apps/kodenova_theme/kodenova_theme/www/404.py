# KodeERP branded 404 (template in 404.html).


def get_context(context):
	context.http_status_code = 404
	context.no_cache = 1
