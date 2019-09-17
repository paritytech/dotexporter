# dotexporter

simple prometheus exporter to expose metrics like block head from rpc of a 
substrate or polkadot node.


metrics that are currently made available:

```
dot_chain_block_number{name="parity-polkadot",version="0.6.0",chain="Kusama CC1",build="0.6.0-d2dac086-x86_64-linux-gnu",block="finalized"} 349301
dot_chain_block_number{name="parity-polkadot",version="0.6.0",chain="Kusama CC1",build="0.6.0-d2dac086-x86_64-linux-gnu",block="head"} 360528
dot_peer_count{name="parity-polkadot",version="0.6.0",chain="Kusama CC1",build="0.6.0-d2dac086-x86_64-linux-gnu"} 25
dot_shouldHavePeers{name="parity-polkadot",version="0.6.0",chain="Kusama CC1",build="0.6.0-d2dac086-x86_64-linux-gnu"} 1
dot_isSyncing{name="parity-polkadot",version="0.6.0",chain="Kusama CC1",build="0.6.0-d2dac086-x86_64-linux-gnu"} 0
dot_specVersion{name="parity-polkadot",version="0.6.0",chain="Kusama CC1",build="0.6.0-d2dac086-x86_64-linux-gnu"} 1001
dot_rpc_healthy{name="parity-polkadot",version="0.6.0",chain="Kusama CC1",build="0.6.0-d2dac086-x86_64-linux-gnu"} 1
```


