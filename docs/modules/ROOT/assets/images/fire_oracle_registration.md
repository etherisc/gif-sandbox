# Fire oracle registration

```mermaid
sequenceDiagram
    actor OP as OracleProvider
    actor IO as InstanceOperator
    participant G as GIF
    participant O as FireOracle
 
    
    IO ->> G: grant role to OracleProvider
    OP->>+ O: deploy FireOracle contract
    OP ->>+ G: propose FireOracle
    G -->>- O: after propose callback
    IO ->>+ G: approve FireOracle
    G -->>- O: after approve callback
```