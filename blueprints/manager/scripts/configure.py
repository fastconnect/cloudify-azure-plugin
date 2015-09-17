from cloudify import ctx

def configure(azure_config):
	ctx.instance.runtime_properties['provider_context'] = {'azure_config': azure_config}