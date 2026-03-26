# Blockchain

The following describes utilizing the blockchain logic as opposed to the "local" master node.
To utilize a "local" master node, set `LOCAL_BLOCKCHAIN=true` in the configuration with appropriate 
configurations.

## Environment Params
In the environment parameter files for each node, the following blockchain options are aviliable.

**Basic Configs**: 
* `LOCAL_BLOCKCHAIN` (default: true) - Whether to run an AnyLog/EdgeLake network with master node **or** using an 
actual blockchain
* `LEDGER_CONN` (default: 127.0.0.1:32048) - TCP conenction information for master node
* `PROVIDER` (default: infura) - SubQuery network participant who is responsible for serving RPC queries for blockchain 
data to their customers. We're using <a herf="https://www.infura.io/" target="_blank>infura</a>
* `PLATFORM` (default: optimism) - Blockchain to use. We're using an off-chain extension (<a herf="https://iq.wiki/wiki/layer-2/" target="_blank">layer-2</a>) 
blockchain named <a herf="https://www.optimism.io/" target="_blank">Optimism</a>

**Advance Configs**
* `BLOCKCHAIN_SYNC` (default: 30 seconds) - How often to sync from blockchain
* `BLOCKCHAIN_SOURCE` (default: master) - Source of where the data is coming from. When `LOCAL_BLOCKCHAIN` is set to _false_, 
value should be set to _blockchain_
* `BLOCKCHAIN_DESTINATION` - Where will the copy of the blockchain be stored locslly
* `PRIVATE_KEY` & `PUBLIC_KEY` - keys to access crypto wallet(s)
* `CHAIN_ID` - Wallet ID

## Process 
The following describe steps to join a network wheen using _Master node_ vs _Blockchain_

## Master Node
1. Declare Params
2. Connect to TCP / REST services
3. 
   * Copy blockchain to local node -- if node type is master, then step is skipped (step in [main](main.al))
   * For Master node - create database (_blockchain_) and table (_ledger_) if does not exist 
4. automatically sync against master every 30 seconds (`SYNC_TIMEE`)

The reason for step 3 is that AnyLog/EdgeLake checks whether the policy exists when try to declare it. 

**File**: [configure_dbms_blockchain.al](database/configure_dbms_blockchain.al)

## Blockchain  
1. Declare Params
2. Connect to TCP / REST services
3. validate keys and credentials exists are set
4. declare / connect to blockchain account
5. set contract
6. set account
7. sync from contract
   * Copy blockchain to local node
   * automatically sync against master every 30 seconds (`SYNC_TIMEE`)

There is no need for a master node when deploying an actual blockchain

**File**: [connect_blockchain.al](connect_blockchain.al)