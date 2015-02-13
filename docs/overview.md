#Hayashi

Hayashi is a C++ implementation of the Stellar protocol. (see stellar_overview.md)

The goal is to be able to scale to 1B accounts and 1000 transactions a second on reasonable hardware.

There are a few major components of the system:

##FBA
This is our implementation of the FBA algorithm.
see http://www.scs.stanford.edu/~dm/noindex/fba.pdf
It has no knowledge of the rest of the system. 

##Herder
This is responsible for interfacing between FBA and th rest of Hayashi. It determines if FBA ballot values are valid or not. 

##Overlay
This is the connection layer. It handles things like: 
- Keeping track of what other peers you are connected to.
- Flooding messages that need to be flooded to the network.
- Fetching things like transaction and quorum sets from the network.
- Trying to keep you connected to the number of peers set in the .cfg 

##Ledger
Handles applying the transaction set that is externalized by FBA. Hands off the resulting changed ledger entries to the CLF.

##CLF
Cannonical Ledger Form. 
Needs to 

##Transactions
The implementaions of all the various transaction types. (see transaction.md)

##crypto

##util
Logging and whatnot

##lib
various 3rd party libaries we use
