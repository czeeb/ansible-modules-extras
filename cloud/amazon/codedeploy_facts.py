#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
module: codedeploy_facts
short_description: Retreives CodeDeploy details using AWS methods
author: "Chris Zeeb(@czeeb)"
extends_documentation_fragment: aws
version_added: "2.1"
requirements:
  - "boto3"
options:
  query:
    required: False
    description:
      - specifies the query action to take
    required: True
    choices:
        - 'list_applications'
        - 'list_deployment_configs'
        - 'list_deployment_groups'
        - 'list_deployment_instances'
        - 'list_deployments'
        - 'list_on_premises_instances'
  application_name:
    requires: False
    description:
      - The application name.  Required for deployment_groups
  next_token:
    required: False
    description:
      - An identifier returned from a previous list request when the list is sufficiently long.  Used to return the next set in the list.
  deployment_id:
    required: False
    description:
      - The unique ID of a deployment.
  deployment_group_name:
    required: False
    description:
      - The name of an existing deployment group for the specified application.
'''

EXAMPLES = '''
# Get list of all applications
- codedeploy_facts:
    query: list_applications

# Get list of deployment configs
- codedeploy_facts:
    query: list_deployment_configs

# Get list of deployment groups for an application
- codedeploy_facts:
    query: list_deployment_groups
    application_name: TestApplication

# Get list of instances a deployment was run on
- codedeploy_facts:
    query: list_deployment_instances
    deployment_id: d-74Y1HLWZC

# Get list of deployments
- codedeploy_facts:
    query: list_deployments

# Get list of deployments for a specific deployment group and application
- codedeploy_facts:
    query: list_deployments
    application_name: TestApplication
    deployment_group_name: Production

# Get list of on-premises instances
- codedeploy_facts:
    query: list_on_premises_instances
'''

try:
    import json
    import boto
    import botocore
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


def list_applications(client, module):
    params = dict()

    if module.params.get('next_token'):
        params['nextToken'] = module.params.get('next_token')

    results = client.list_applications(**params)
    return results


def list_deployment_configs(client, module):
    params = dict()

    if module.params.get('next_token'):
        params['nextToken'] = module.params.get('next_token')

    results = client.list_deployment_configs(**params)
    return results


def list_deployment_groups(client, module):
    params = dict()

    if module.params.get('application_name'):
        params['applicationName'] = module.params.get('application_name')
    else:
        module.fail_json(msg="application_name is required")

    if module.params.get('next_token'):
        params['nextToken'] = module.params.get('next_token')

    results = client.list_deployment_groups(**params)
    return results


def list_deployment_instances(client, module):
    params = dict()

    if module.params.get('deployment_id'):
        params['deploymentId'] = module.params.get('deployment_id')
    else:
        module.fail_json(msg="deployment_id is required")

    if module.params.get('instance_status_filter'):
        params['instanceStatusFilter'] = module.params.get('instance_status_filter')

    if module.params.get('next_token'):
        params['nextToken'] = module.params.get('next_token')

    results = client.list_deployment_instances(**params)
    return results


def list_deployments(client, module):
    params = dict()

    if module.params.get('deployment_group_name') and module.params.get('application_name'):
        params['applicationName'] = module.params.get('application_name')
        params['deploymentGroupName'] = module.params.get('deployment_group_name')
    elif module.params.get('deployment_group_name') and not module.params.get('application_name'):
        module.fail_json(msg="application_name is required when deployment_group_name used")
    elif not module.params.get('deployment_group_name') and module.params.get('application_name'):
        module.fail_json(msg="deployment_group_name is required when application_name used")

    if module.params.get('next_token'):
        params['nextToken'] = module.params.get('next_token')

    results = client.list_deployments(**params)
    return results


def list_on_premises_instances(client, module):
    params = dict()

    if module.params.get('registration_status'):
        params['registrationStatus'] = module.params.get('registration-status')

    if module.params.get('next_token'):
        params['nextToken'] = module.params.get('next_token')

    results = client.list_on_premises_instances(**params)
    return results


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        query=dict(choices=[
            'list_applications',
            'list_deployment_configs',
            'list_deployment_groups',
            'list_deployment_instances',
            'list_deployments',
            'list_on_premises_instances'
        ], required=True),
        next_token=dict(),
        application_name=dict(),
        deployment_id=dict(),
        deployment_group_name=dict(),
        registration_status=dict(),
        )
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # Validate Requirements
    if not (HAS_BOTO or HAS_BOTO3):
        module.fail_json(msg='json and boto/boto3 is required.')

    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        codedeploy = boto3_conn(module, conn_type='client', resource='codedeploy', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except boto.exception.NoAuthHandlerFound, e:
        module.fail_json(msg="Can't authorize connection - "+str(e))

    invocations = {
        'list_applications': list_applications,
        'list_deployment_configs': list_deployment_configs,
        'list_deployment_groups': list_deployment_groups,
        'list_deployment_instances': list_deployment_instances,
        'list_deployments': list_deployments,
        'list_on_premises_instances': list_on_premises_instances,
    }
    results = invocations[module.params.get('query')](codedeploy, module)

    module.exit_json(**results)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()
