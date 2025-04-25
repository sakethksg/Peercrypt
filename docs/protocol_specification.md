## 1.3 Protocol State Machine

The PeerCrypt File Transfer Protocol follows a well-defined state machine that ensures reliable, ordered and secure file transfers. Each transfer session transitions through the following states:

```
                                  +-------------+
                                  |             |
                                  |    IDLE     |
                                  |             |
                                  +------+------+
                                         |
                                         | INIT_TRANSFER
                                         v
                       ABORT     +-------------+
                 +---------------|             |<--------------+
                 |               | CONNECTING  |               |
                 |               |             |               |
                 |               +------+------+               |
                 |                      |                      |
                 |                      | CONN_ESTABLISHED     |
                 v                      v                      |
         +-------------+        +-------------+                |
         |             |        |             |                |
         |    ERROR    |<-------|  TRANSFER   +---+            |
         |             |  ERROR |             |   |            |
         +------+------+        +------+------+   |            |
                |                      |          | RETRY      |
                |                      | COMPLETE |            |
                |                      v          |            |
                |              +-------------+    |            |
                |              |             |    |            |
                |              | VALIDATING  |----+            |
                |              |             |                 |
                |              +------+------+                 |
                |                     |                        |
                |                     | VALIDATION_FAILED      |
                +---------------------|                        |
                                      | VALIDATION_PASSED      |
                                      v                        |
                              +-------------+                  |
                              |             |                  |
                              | COMPLETED   +------------------+
                              |             |    RESTART
                              +-------------+
```

### State Descriptions:

| State | Description | Entry Events | Exit Events |
|-------|-------------|--------------|-------------|
| **IDLE** | Initial state when no transfer is in progress | System initialization, Transfer completion | `INIT_TRANSFER` message |
| **CONNECTING** | Establishing connection with peer | `INIT_TRANSFER` message | `CONN_ESTABLISHED` event or timeout |
| **TRANSFER** | Actively transferring file chunks | Connection establishment | `COMPLETE` on full transfer, `ERROR` on failure |
| **VALIDATING** | Verifying integrity of transferred file | All chunks received | `VALIDATION_PASSED` or `VALIDATION_FAILED` events |
| **ERROR** | Error handling state | Any error condition | Manual restart or automatic retry |
| **COMPLETED** | Successful transfer completion | File validation success | New `INIT_TRANSFER` or system shutdown |

### Key Transitions:

- **TRANSFER → VALIDATING**: Occurs when the final chunk is received and CRC validation begins
- **VALIDATING → ERROR**: Triggered by checksum mismatch or cryptographic signature failure
- **ERROR → CONNECTING**: Automatic retry mechanism for recoverable errors
- **COMPLETED → CONNECTING**: Manual restart of a new transfer session

### Error Handling:
The protocol implements a comprehensive error recovery mechanism with:
- Automatic retries for transient network failures
- Exponential backoff for connection attempts (100ms, 200ms, 400ms...)
- State persistence for recovery after unexpected disconnections
- Partial transfer resumption capabilities

This state machine ensures that all file transfers maintain atomicity and consistency, even in unreliable network conditions. 