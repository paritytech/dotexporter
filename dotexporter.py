#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# expose vital data of dot nodes for prometheus


from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import os



NODE_URL = os.environ.get("NODE_URL", "http://localhost:9933")
LISTEN   = os.environ.get("LISTEN", "0.0.0.0")
PORT     = int(os.environ.get("PORT", "8000"))
DEBUG    = bool(os.environ.get("DEBUG", False))



class DotExporter(BaseHTTPRequestHandler):

  spec = {}

  def set_spec(self):
    try:
      spec = {}
      spec['name']    = self.query("system_name")
      spec['version'] = self.query("system_version")
      spec['chain']   = self.query("system_chain")
      try:
        with open('/polkaversion/version') as v:
          spec['build'] = v.readline().strip().split(' ')[1]
        with open('/polkaversion/substrate-ref') as sr:
          spec['substrate_ref'] = '-'.join([l.strip() for l in sr.readlines()])
      except:
        pass
      DotExporter.spec = spec
    except:
      DotExporter.spec = {}


  def __init__(self, *args):
    self.set_spec()
    BaseHTTPRequestHandler.__init__(self, *args)

  def log_message(self, format, *args):
    msg = format % args
    if hasattr(self, 'msg'):
      msg += ' :: %s' % self.msg
    if hasattr(self, 'headers') and self.headers.get('Origin'):
      msg += ' [%s]' % self.headers.get('Origin')
    BaseHTTPRequestHandler.log_message(self, msg)


  def query(self, method, params = []):
    header  = { 'Content-Type': 'application/json', 'Accept': 'application/json' }
    payload = { 'jsonrpc': '2.0', 'method': method, 'params': params, 'id': 0 }

    r = requests.post(NODE_URL, json=payload, headers=header)

    try:
      return r.json()['result']
    except:
      self.msg = r.text


  def send(self, text = "", status = 200):
    self.send_response(status)
    self.send_header("Content-type", "text/plain")
    self.end_headers()
    self.wfile.write(str.encode(text))



  def do_GET(self):

    if self.path == '/metrics':
      if not DotExporter.spec:
        self.set_spec()
      # maybe implement system_networkState in the future
      m = []
      try:
        name    = self.query("system_name")
        version = self.query("system_version")
        chain   = self.query("system_chain")

        chain_getHeader = self.query("chain_getHeader")
        system_health   = self.query("system_health")
        runtime_version = self.query("state_getRuntimeVersion")

        try:
          chain_getFinalizedHead   = self.query("chain_getFinalizedHead")
          chain_FinalizedHeadBlock = self.query("chain_getBlock", [chain_getFinalizedHead])
          m.append({
            'name': 'dot_chain_block_number',
            'prop': { 'block': 'finalized' },
            'value': int(chain_FinalizedHeadBlock['block']['header']['number'], 16)
          })
        except:
          pass

        m.append({
          'name': 'dot_chain_block_number',
          'prop': { 'block': 'head' },
          'value': int(chain_getHeader['number'], 16)
        })
        m.append({
          'name': 'dot_peer_count',
          'value': int(system_health["peers"])
        })
        m.append({
          'name': 'dot_shouldHavePeers',
          'value': int(system_health["shouldHavePeers"])
        })
        m.append({
          'name': 'dot_isSyncing',
          'value': int(system_health["isSyncing"])
        })
        m.append({
          'name': 'dot_specVersion',
          'value': int(runtime_version["specVersion"])
        })
        m.append({
          'name': 'dot_rpc_healthy',
          'value': 1
        })
      except:
        m.append({
          'name': 'dot_rpc_healthy',
          'value': 0
        })

      metrics = ''
      for i in m:
        prop = ','.join([ f'{k}="{v}"' for k,v in { **DotExporter.spec, **i.get('prop', {})}.items()])
        if prop: prop = f'{{{prop}}}'
        metrics += f"{i['name']}{prop} {i['value']}\n"
      return self.send(metrics)

    elif self.path == '/health':

      if DEBUG and self.headers.get('Origin') == 'dotexporter':
        return self.send(status = 200)

      try:
        system_health = self.query("system_health")
        assert('peers' in system_health and 'shouldHavePeers' in system_health)
      except:
        return self.send(status = 502)

      if system_health["peers"] < 2 and system_health["shouldHavePeers"] == True:
        self.msg = "system_health: peers %s, shouldHavePeers: %s" \
            % (system_health["peers"], system_health["shouldHavePeers"])
        return self.send(status = 500)

      self.msg = '%s peers' % system_health["peers"]
      return self.send("OK %s\n" % system_health["peers"])
    else:
      return self.send("substrate/polkadot node monitoring\n")


if __name__ == '__main__':
  httpd = HTTPServer((LISTEN, PORT), DotExporter)
  print("Serving requests on %s:%s" % (LISTEN, PORT))
  httpd.serve_forever()


