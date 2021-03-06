import os
import sys
import json
import shutil
import importlib
import subprocess
import re
import time
from sandstone import settings



DPORT = '49160'
BASE_URL = 'http://localhost:{}'.format(DPORT)

sandstone_mod = __import__('sandstone',fromlist=[''])
core_path = os.path.join(sandstone_mod.__path__[0],'client','sandstone','')

print "Building base container..."
test_start = time.time()
# Build Sandstone IDE image
base_img_path = os.path.abspath(os.path.join(sandstone_mod.__path__[0],'..'))
os.chdir(base_img_path)
subprocess.call(['docker','build','-q','-t','sandstone','.'])

for spec in settings.APP_SPECIFICATIONS:
    # if an app name was passed to script, only
    # test the named app
    if len(sys.argv) > 1:
        test_app = sys.argv[1]
        if not spec['NG_MODULE_NAME'] == test_app:
            continue
    # get the module object using the module name
    mod_path = spec['PY_MODULE_PATH']
    e2e_dir = os.path.join(mod_path,'tests','e2e')
    # Check if there are E2E tests to run
    if os.path.exists(e2e_dir):
        if len(os.listdir(e2e_dir)) == 0:
            continue
        if os.listdir(e2e_dir) == ['Dockerfile']:
            continue
    else:
        continue
    mod_spec_path = os.path.join(e2e_dir,'**','*.spec.js')

    # Define file_list for app
    file_list = []
    file_list.append(mod_spec_path)

    # Format protractor.environment.js
    fmt_dict = {
        'base_url': BASE_URL,
        'file_list': json.dumps(file_list),
    }

    client_path = os.path.join(sandstone_mod.__path__[0],'client')
    with open(os.path.join(client_path,'protractor.environment.js.tpl')) as prot_env_tpl:
        file_contents = prot_env_tpl.read()

    fmt_contents = file_contents%fmt_dict
    with open(os.path.join(client_path,'protractor.environment.js'), 'w') as prot_env:
        prot_env.write(fmt_contents)

    # Build and run Docker container for app
    print "Building {} container...".format(spec['NG_MODULE_NAME'])
    os.chdir(e2e_dir)
    subprocess.call(['docker','build','-q','-t',spec['NG_MODULE_NAME'],'.'])
    subprocess.call([
        'docker','run','-p','49160:8888','-d','--user=sandstone',
        spec['NG_MODULE_NAME']
        ])

    # Run tests
    os.chdir(sandstone_mod.__path__[0])
    os.chdir(client_path)
    subprocess.call(['npm','run','protractor'])

    # Kill app container
    subprocess.call('docker stop $(docker ps -q)',shell=True)

test_end = time.time()
elapsed = test_end - test_start
print "Test suite ran in {} seconds".format(elapsed)
