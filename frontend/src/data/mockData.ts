import {
  BugSubmission,
  DiagnosisReport,
  AgentExecutionLog,
  KnowledgeBaseStats,
  Dataset,
  SearchResultItem,
  SystemArchitecture
} from '../types';

export interface BugPreset {
  id: string;
  name: string;
  project: 'Mozilla' | 'Eclipse' | 'Apache';
  icon: string;
  badge: 'Critical' | 'Major' | 'Blocker';
  title: string;
  language: string;
  framework: string;
  severity: 'critical' | 'high' | 'medium';
  priority: 'p1' | 'p2' | 'p3';
  description: string;
  stack_trace: string;
  error_logs: string;
}

export const BUG_PRESETS: BugPreset[] = [
  {
    id: 'preset-mozilla-ipc',
    name: 'Mozilla IPC Memory Out-of-Bounds',
    project: 'Mozilla',
    icon: '🦊',
    badge: 'Blocker',
    title: 'ContentChild::RecvUpdate crash with SIGSEGV in IPC message deserializer',
    language: 'C++',
    framework: 'Gecko IPC',
    severity: 'critical',
    priority: 'p1',
    description: 'When loading heavily populated canvas DOM elements across multi-process tabs, ContentChild crashes abruptly with SIGSEGV during IPC message deserialization. Memory profiler indicates a buffer overrun in the shared memory message payload buffer.',
    stack_trace: `#0  0x00007fff8ac29130 in mozilla::ipc::MessageChannel::DispatchMessage (this=0x7fff800410, msg=...) at /ipc/glue/MessageChannel.cpp:2184
#1  0x00007fff8ac28d10 in mozilla::dom::ContentChild::RecvUpdate (this=0x7fff800100, actorId=42, payload=...) at /dom/ipc/ContentChild.cpp:312
#2  0x00007fff8ac1f440 in mozilla::ipc::SharedMemory::ReadBuffer (this=0x7fff800920, offset=1048576, size=4096) at /ipc/chromium/src/base/shared_memory_posix.cc:294
#3  0x00007fff89f10420 in nsThread::ProcessNextEvent (this=0x7fff900200, mayWait=false, result=0x7fff8a) at /xpcom/threads/nsThread.cpp:1180
#4  0x00007fff89f10b50 in NS_ProcessNextEvent (thread=0x7fff900200, mayWait=false) at /xpcom/threads/nsThreadUtils.cpp:465`,
    error_logs: `[14:22:01.402] [IPC-Worker-2] WARN: MessageChannel received oversized frame 4194304 bytes exceeding MAX_SAFE_DESERIALIZE_BOUND.
[14:22:01.408] [ContentChild] ERROR: Buffer bounds violation in actor id 42: attempted offset 1048576 on buffer size 1048576.
[14:22:01.411] [System-Trap] Fatal signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x00007fff8ac29130`
  },
  {
    id: 'preset-eclipse-workspace',
    name: 'Eclipse Workspace NPE Deadlock',
    project: 'Eclipse',
    icon: '🌑',
    badge: 'Critical',
    title: 'NullPointerException in Workspace.save() during background auto-build synchronization',
    language: 'Java',
    framework: 'Eclipse Core Resources',
    severity: 'critical',
    priority: 'p1',
    description: 'During scheduled background auto-build or workspace resource refresh, Workspace.save() throws NullPointerException when accessing resource tree node description metadata. This results in workspace lock deadlock requiring forceful IDE restart.',
    stack_trace: `java.lang.NullPointerException: Cannot invoke "org.eclipse.core.internal.resources.ResourceInfo.getNodeId()" because "info" is null
	at org.eclipse.core.internal.resources.Workspace.save(Workspace.java:2348)
	at org.eclipse.core.internal.resources.SaveManager.save(SaveManager.java:1187)
	at org.eclipse.core.internal.resources.Workspace.run(Workspace.java:2295)
	at org.eclipse.core.internal.events.AutoBuildJob.run(AutoBuildJob.java:242)
	at org.eclipse.core.internal.jobs.Worker.run(Worker.java:63)`,
    error_logs: `2026-11-13 14:15:22.812 [Worker-3: Auto-build] ERROR org.eclipse.core.runtime - An internal error occurred during: "Building workspace".
java.lang.NullPointerException: Cannot invoke "org.eclipse.core.internal.resources.ResourceInfo.getNodeId()"
	at org.eclipse.core.internal.resources.Workspace.save(Workspace.java:2348)
2026-11-13 14:15:22.819 [Worker-3: Auto-build] WARN org.eclipse.core.jobs - Job AutoBuildJob held workspace rule lock and failed to release safely.`
  },
  {
    id: 'preset-apache-spark',
    name: 'Apache Spark Shuffle OOM Crash',
    project: 'Apache',
    icon: '⚡',
    badge: 'Major',
    title: 'SparkException: Shuffle block sync timeout and ExecutorLostFailure during heavy sort-merge join',
    language: 'Scala / Java',
    framework: 'Apache Spark 3.4',
    severity: 'high',
    priority: 'p2',
    description: 'Executor nodes drop unexpectedly during Stage 4 sort-merge join shuffle fetch. Heartbeat receiver marks executor as timed out, followed by java.lang.OutOfMemoryError: Java heap space during UnsafeExternalSorter spill.',
    stack_trace: `org.apache.spark.SparkException: Shuffle block sync timeout: Block rdd_42_0 fetch failed after 3 retries
	at org.apache.spark.storage.BlockManager.getRemoteBlock(BlockManager.scala:872)
	at org.apache.spark.shuffle.sort.UnsafeExternalSorter.spill(UnsafeExternalSorter.java:264)
	at org.apache.spark.util.collection.unsafe.sort.RadixSort.sort(RadixSort.java:78)
	at org.apache.spark.sql.execution.joins.SortMergeJoinExec.doExecute(SortMergeJoinExec.scala:142)
	at org.apache.spark.scheduler.DAGScheduler.handleTaskCompletion(DAGScheduler.scala:1428)`,
    error_logs: `2026-11-13T14:02:11,402 ERROR [task-result-getter-0] scheduler.TaskSetManager: Task 4.0 in stage 4.0 failed 4 times; aborting job
2026-11-13T14:02:11,408 ERROR [Executor task launch worker for task 4] executor.Executor: Exception in task 4.0 in stage 4.0 (TID 128)
java.lang.OutOfMemoryError: Java heap space in org.apache.spark.memory.UnifiedMemoryManager
2026-11-13T14:02:11,415 WARN [HeartbeatReceiver] scheduler.HeartbeatReceiver: Removing executor 4 with no recent heartbeats: 120521 ms`
  }
];

export const INITIAL_SUBMISSIONS: BugSubmission[] = [
  {
    id: 'sub-moz-8910',
    title: 'ContentChild::RecvUpdate crash with SIGSEGV in IPC message deserializer',
    description: 'When loading heavily populated canvas DOM elements across multi-process tabs, ContentChild crashes abruptly with SIGSEGV during IPC message deserialization.',
    stack_trace: `#0  0x00007fff8ac29130 in mozilla::ipc::MessageChannel::DispatchMessage\n#1  0x00007fff8ac28d10 in mozilla::dom::ContentChild::RecvUpdate\n#2  0x00007fff8ac1f440 in mozilla::ipc::SharedMemory::ReadBuffer`,
    error_logs: `[IPC-Worker-2] WARN: MessageChannel received oversized frame 4194304 bytes exceeding MAX_SAFE_DESERIALIZE_BOUND.`,
    programming_language: 'C++',
    framework: 'Gecko IPC',
    severity: 'critical',
    priority: 'p1',
    status: 'analyzed',
    created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    updated_at: new Date(Date.now() - 3600000 * 2).toISOString(),
  },
  {
    id: 'sub-ecl-4125',
    title: 'NullPointerException in Workspace.save() during background auto-build synchronization',
    description: 'During scheduled background auto-build, Workspace.save() throws NullPointerException when accessing resource tree description metadata.',
    stack_trace: `java.lang.NullPointerException: Cannot invoke ResourceInfo.getNodeId()\n\tat org.eclipse.core.internal.resources.Workspace.save(Workspace.java:2348)`,
    error_logs: `ERROR org.eclipse.core.runtime - An internal error occurred during: "Building workspace".`,
    programming_language: 'Java',
    framework: 'Eclipse Core Resources',
    severity: 'critical',
    priority: 'p1',
    status: 'analyzed',
    created_at: new Date(Date.now() - 3600000 * 14).toISOString(),
    updated_at: new Date(Date.now() - 3600000 * 14).toISOString(),
  },
  {
    id: 'sub-spk-3829',
    title: 'SparkException: Shuffle block sync timeout and ExecutorLostFailure',
    description: 'Executor nodes drop unexpectedly during Stage 4 sort-merge join shuffle fetch.',
    stack_trace: `org.apache.spark.SparkException: Shuffle block sync timeout\n\tat org.apache.spark.storage.BlockManager.getRemoteBlock(BlockManager.scala:872)`,
    programming_language: 'Scala',
    framework: 'Apache Spark',
    severity: 'high',
    priority: 'p2',
    status: 'analyzed',
    created_at: new Date(Date.now() - 3600000 * 26).toISOString(),
    updated_at: new Date(Date.now() - 3600000 * 26).toISOString(),
  }
];

export const MOCK_DIAGNOSIS_REPORTS: Record<string, DiagnosisReport> = {
  'sub-moz-8910': {
    id: 'diag-moz-8910',
    submission_id: 'sub-moz-8910',
    status: 'completed',
    overall_confidence: 0.94,
    created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    updated_at: new Date(Date.now() - 3600000 * 2).toISOString(),
    triage_result: {
      category: 'Memory Management / IPC Deserialization',
      severity: 'Critical / Blocker',
      priority: 'P1 - Immediate Fix',
      programming_language: 'C++',
      framework: 'Gecko IPC / SharedMemory POSIX',
      completeness_score: 96,
      missing_information: [
        'Client GPU acceleration state (WebRender enabled vs disabled)',
        'Detailed OS kernel memory overcommit sysctl setting'
      ]
    },
    log_analysis_result: {
      has_stack_trace: true,
      exception_type: 'SIGSEGV (SEGV_MAPERR)',
      error_message: 'Buffer bounds violation: attempted offset 1048576 on buffer size 1048576',
      stack_frames: [
        { file: '/ipc/glue/MessageChannel.cpp', line: 2184, function: 'mozilla::ipc::MessageChannel::DispatchMessage' },
        { file: '/dom/ipc/ContentChild.cpp', line: 312, function: 'mozilla::dom::ContentChild::RecvUpdate' },
        { file: '/ipc/chromium/src/base/shared_memory_posix.cc', line: 294, function: 'mozilla::ipc::SharedMemory::ReadBuffer' },
        { file: '/xpcom/threads/nsThread.cpp', line: 1180, function: 'nsThread::ProcessNextEvent' }
      ],
      suspect_files: [
        'dom/ipc/ContentChild.cpp',
        'ipc/chromium/src/base/shared_memory_posix.cc'
      ],
      technical_evidence: [
        'Oversized frame payload of 4194304 bytes encountered without prior length validation check',
        'Direct pointer dereference in SharedMemory::ReadBuffer without bounds guard',
        'Exact matching crash signature in historical defect MOZ-1482910'
      ]
    },
    duplicate_detection_result: {
      is_duplicate: true,
      highest_similarity: 0.942,
      potential_duplicates: [
        {
          defect_id: 'MOZ-1482910',
          source_repo: 'Mozilla Bugzilla',
          original_issue_id: '1482910',
          title: 'Crash in ContentChild::RecvUpdate when deserializing large canvas update buffer',
          similarity_score: 0.942,
          retrieval_method: 'Hybrid (Dense bge-small-en + BM25 Reciprocal Rank Fusion)'
        },
        {
          defect_id: 'MOZ-1520114',
          source_repo: 'Mozilla Bugzilla',
          original_issue_id: '1520114',
          title: 'SharedMemory buffer overflow during high frequency IPC stream transmission',
          similarity_score: 0.814,
          retrieval_method: 'Dense Semantic Vector Search'
        }
      ]
    },
    root_cause_result: {
      identified_root_cause: 'Off-by-one buffer boundary check in ContentChild::RecvUpdate allows reading past the end of the shared memory payload during multi-threaded IPC dispatch.',
      explanation: 'When a tab renders dense DOM canvas trees, the IPC serialization protocol divides data into chunks of 1024KB. The boundary validator in ContentChild.cpp checked (offset > buffer_size) rather than (offset + read_size > buffer_size), causing an out-of-bounds pointer read when exactly hitting the boundary buffer limit.',
      confidence: 0.92,
      supporting_evidence: [
        'Crash occurs at exact 1MB boundary (offset 1048576)',
        'Stack frame #2 confirms ReadBuffer attempted reading 4096 bytes beyond allocated slice',
        'Historical defect MOZ-1482910 documented identical reproduction step and confirmed resolution'
      ],
      historical_matches: [
        {
          defect_id: 'MOZ-1482910',
          source_repo: 'Mozilla Bugzilla',
          original_issue_id: '1482910',
          title: 'Crash in ContentChild::RecvUpdate when deserializing large canvas update buffer',
          similarity_score: 0.942,
          resolution: 'FIXED in changeset c91e4a1',
          url: 'https://bugzilla.mozilla.org/show_bug.cgi?id=1482910'
        }
      ]
    },
    remediation_result: {
      rationale: 'Add strict bounds checking before attempting to read bytes from the SharedMemory segment, and introduce a graceful IPC error return rather than an unhandled segmentation fault.',
      historical_references: [
        {
          defect_id: 'MOZ-1482910',
          source_repo: 'Mozilla Bugzilla',
          original_issue_id: '1482910',
          title: 'Buffer boundary safety patch in Gecko IPC ContentChild',
          similarity_score: 0.942,
          resolution: 'FIXED',
          url: 'https://bugzilla.mozilla.org/show_bug.cgi?id=1482910'
        }
      ],
      verified_fixes: [
        {
          title: 'Patch ContentChild.cpp Buffer Check & Validate Payload Bounds',
          description: 'Enforce that both start offset and chunk length do not exceed total mapped shared memory space before invoking ReadBuffer.',
          is_verified_from_history: true,
          source_defect_id: 'MOZ-1482910',
          diff_snippet: `--- a/dom/ipc/ContentChild.cpp
+++ b/dom/ipc/ContentChild.cpp
@@ -309,7 +309,9 @@ bool ContentChild::RecvUpdate(const uint32_t actorId, const IPC::Payload& payload)
 {
+    // Guard against buffer overrun when payload approaches mapped limit
+    if (MOZ_UNLIKELY(payload.offset + payload.size > mSharedBuffer->Size())) {
+        NS_WARNING("Refusing to read beyond SharedMemory boundary");
+        return false;
+    }
-    mSharedBuffer->ReadBuffer(payload.offset, payload.size);
+    mSharedBuffer->ReadBufferSafe(payload.offset, payload.size);
     return true;
 }`
        }
      ],
      suggested_fixes: [
        {
          title: 'Configure IPC Message Chunk Cap in Preference System',
          description: 'Set dom.ipc.canvas.max_chunk_size_kb to 512 to prevent oversized single messages from overwhelming shared memory buffers.',
          is_verified_from_history: false,
          diff_snippet: `user_pref("dom.ipc.canvas.max_chunk_size_kb", 512);`
        }
      ]
    }
  },
  'sub-ecl-4125': {
    id: 'diag-ecl-4125',
    submission_id: 'sub-ecl-4125',
    status: 'completed',
    overall_confidence: 0.96,
    created_at: new Date(Date.now() - 3600000 * 14).toISOString(),
    updated_at: new Date(Date.now() - 3600000 * 14).toISOString(),
    triage_result: {
      category: 'Concurrency / Workspace Resource Lock',
      severity: 'Critical / Blocker',
      priority: 'P1',
      programming_language: 'Java',
      framework: 'Eclipse Core Resources 3.8',
      completeness_score: 94,
      missing_information: ['Workspace snapshot frequency settings (.metadata/.plugins)']
    },
    log_analysis_result: {
      has_stack_trace: true,
      exception_type: 'java.lang.NullPointerException',
      error_message: 'Cannot invoke ResourceInfo.getNodeId() because info is null',
      stack_frames: [
        { file: 'Workspace.java', line: 2348, function: 'org.eclipse.core.internal.resources.Workspace.save' },
        { file: 'SaveManager.java', line: 1187, function: 'org.eclipse.core.internal.resources.SaveManager.save' },
        { file: 'AutoBuildJob.java', line: 242, function: 'org.eclipse.core.internal.events.AutoBuildJob.run' }
      ],
      suspect_files: ['org/eclipse/core/internal/resources/Workspace.java'],
      technical_evidence: [
        'Element tree lookup in ResourceTree returned null during concurrent workspace refresh',
        'AutoBuildJob crashed while holding write lock, creating permanent IDE lockup'
      ]
    },
    duplicate_detection_result: {
      is_duplicate: true,
      highest_similarity: 0.958,
      potential_duplicates: [
        {
          defect_id: 'ECLIPSE-412581',
          source_repo: 'Eclipse Bugzilla',
          original_issue_id: '412581',
          title: 'NPE in Workspace.save() when resource deleted during background auto-build',
          similarity_score: 0.958,
          retrieval_method: 'Hybrid Dense + BM25'
        }
      ]
    },
    root_cause_result: {
      identified_root_cause: 'Unsynchronized access between ResourceTree.getElementData() and background file deletion events caused an unpopulated ResourceInfo handle to be passed into Workspace.save().',
      explanation: 'When an auto-build executes concurrently with an external file deletion, the resource node in the ElementTree is cleared before the save manager finishes iterating over the tree.',
      confidence: 0.96,
      supporting_evidence: [
        'Line 2348 directly accesses info.getNodeId() without null assertion',
        'Verified in Eclipse Platform bug 412581 commit history'
      ],
      historical_matches: [
        {
          defect_id: 'ECLIPSE-412581',
          source_repo: 'Eclipse Bugzilla',
          original_issue_id: '412581',
          title: 'NPE in Workspace.save() when resource deleted during auto-build',
          similarity_score: 0.958,
          resolution: 'FIXED in commit b3192e',
          url: 'https://bugs.eclipse.org/bugs/show_bug.cgi?id=412581'
        }
      ]
    },
    remediation_result: {
      rationale: 'Verify resource existence and null-check ResourceInfo before retrieving nodeId; release workspace lock in finally block.',
      historical_references: [
        {
          defect_id: 'ECLIPSE-412581',
          source_repo: 'Eclipse Bugzilla',
          original_issue_id: '412581',
          title: 'Fix null check in Workspace.save',
          similarity_score: 0.958,
          resolution: 'FIXED'
        }
      ],
      verified_fixes: [
        {
          title: 'Add Defensive Null Check in Workspace.save()',
          description: 'Gracefully skip vanished resource nodes during tree serialization.',
          is_verified_from_history: true,
          source_defect_id: 'ECLIPSE-412581',
          diff_snippet: `--- a/org/eclipse/core/internal/resources/Workspace.java
+++ b/org/eclipse/core/internal/resources/Workspace.java
@@ -2346,6 +2346,8 @@ public IStatus save(boolean full, IProgressMonitor monitor) {
         ResourceInfo info = tree.getResourceInfo(path, false, false);
+        if (info == null) {
+            continue; // Node was deleted concurrently; skip safely
+        }
         String nodeId = info.getNodeId();`
        }
      ],
      suggested_fixes: []
    }
  }
};

export const MOCK_HISTORICAL_DEFECTS: SearchResultItem[] = [
  {
    defect_id: 'MOZ-1482910',
    original_issue_id: '1482910',
    source_repo: 'Mozilla Bugzilla',
    title: 'Crash in ContentChild::RecvUpdate when deserializing large canvas update buffer',
    description: 'Content process terminates with SIGSEGV when receiving large serialized array buffers exceeding 1MB from GPU process.',
    stack_trace: `mozilla::ipc::MessageChannel::DispatchMessage\nmozilla::dom::ContentChild::RecvUpdate\nmozilla::ipc::SharedMemory::ReadBuffer`,
    resolution: 'FIXED',
    status: 'CLOSED',
    programming_language: 'C++',
    similarity_score: 0.942,
    retrieval_method: 'Hybrid (bge-small-en + BM25 RRF)',
    matched_chunk: 'Buffer boundary safety check added before invoking ReadBuffer on SharedMemory'
  },
  {
    defect_id: 'ECLIPSE-412581',
    original_issue_id: '412581',
    source_repo: 'Eclipse Bugzilla',
    title: 'NPE in Workspace.save() when resource deleted during background auto-build',
    description: 'Workspace.save fails with NullPointerException during scheduled workspace state snapshot if an external tool deleted a project file concurrently.',
    stack_trace: `java.lang.NullPointerException\n\tat org.eclipse.core.internal.resources.Workspace.save(Workspace.java:2348)`,
    resolution: 'FIXED',
    status: 'VERIFIED',
    programming_language: 'Java',
    similarity_score: 0.958,
    retrieval_method: 'Hybrid (bge-small-en + BM25 RRF)',
    matched_chunk: 'Skip missing resource info node during ElementTree traversal in Workspace save'
  },
  {
    defect_id: 'SPARK-38291',
    original_issue_id: 'SPARK-38291',
    source_repo: 'Apache Jira',
    title: 'Shuffle block sync timeout during DAGScheduler stage sort-merge join',
    description: 'Executors running heavy memory-intensive joins run out of heap space during RadixSort and drop heartbeat connections.',
    stack_trace: `org.apache.spark.SparkException: Shuffle block sync timeout\n\tat org.apache.spark.storage.BlockManager.getRemoteBlock`,
    resolution: 'FIXED',
    status: 'RESOLVED',
    programming_language: 'Scala',
    similarity_score: 0.895,
    retrieval_method: 'Dense Semantic Vector Search',
    matched_chunk: 'UnifiedMemoryManager spill threshold tuned to avoid sudden executor OOM'
  },
  {
    defect_id: 'MOZ-1390142',
    original_issue_id: '1390142',
    source_repo: 'Mozilla Bugzilla',
    title: 'Use-after-free in nsDocShell::Destroy when closing pop-up windows',
    description: 'DocShell teardown fails to unregister event listeners, resulting in memory corruption during subsequent garbage collection sweep.',
    stack_trace: `nsDocShell::Destroy\nnsGlobalWindowInner::FreeInnerObjects`,
    resolution: 'FIXED',
    status: 'VERIFIED',
    programming_language: 'C++',
    similarity_score: 0.781,
    retrieval_method: 'Dense Semantic Vector Search',
    matched_chunk: 'Explicitly clear parent document pointer before invoking destructor'
  },
  {
    defect_id: 'HADOOP-18290',
    original_issue_id: 'HADOOP-18290',
    source_repo: 'Apache Jira',
    title: 'IPC Client connection pool deadlocks under concurrent authentication retry storms',
    description: 'When Kerberos tokens expire under heavy MapReduce throughput, all worker threads block on Client.getConnection lock.',
    stack_trace: `org.apache.hadoop.ipc.Client.getConnection\norg.apache.hadoop.ipc.Client$Connection.setupIOstreams`,
    resolution: 'FIXED',
    status: 'CLOSED',
    programming_language: 'Java',
    similarity_score: 0.824,
    retrieval_method: 'Sparse BM25 Exact Frame Match',
    matched_chunk: 'Refactor connection pool lock to fine-grained concurrent map'
  },
  {
    defect_id: 'ECLIPSE-389102',
    original_issue_id: '389102',
    source_repo: 'Eclipse Bugzilla',
    title: 'ConcurrentModificationException in PluginModelManager during bundle activation',
    description: 'Adding dynamic OSGi bundles while IDE initializes causes concurrent modification in bundle listener registry.',
    stack_trace: `java.util.ConcurrentModificationException\n\tat org.eclipse.pde.internal.core.PluginModelManager.bundleChanged`,
    resolution: 'FIXED',
    status: 'VERIFIED',
    programming_language: 'Java',
    similarity_score: 0.849,
    retrieval_method: 'Hybrid (bge-small-en + BM25 RRF)',
    matched_chunk: 'Wrap bundle change listener array with CopyOnWriteArrayList'
  }
];

export const MOCK_KB_STATS: KnowledgeBaseStats = {
  total_datasets: 3,
  total_defects: 219585,
  total_chunks: 684200,
  total_embeddings: 684200,
  by_source: {
    'Mozilla Bugzilla': 119585,
    'Eclipse Foundation': 68000,
    'Apache Jira': 32000
  },
  by_language: {
    'C++': 98200,
    'Java': 89100,
    'Python': 18500,
    'JavaScript/TS': 13785
  },
  vector_index_status: 'Healthy (Qdrant HNSW cosine 384-d)',
  bm25_index_status: 'Indexed (rank-bm25 684k chunks)'
};

export const MOCK_ARCHITECTURE: SystemArchitecture = {
  platform_name: 'TraceIQ',
  milestone: 'Milestone 1 Foundation + M2 Multi-Agent Engine',
  pipeline_workflow: [
    'Raw Defect Ingestion (Paste or Upload .log/.txt/.json)',
    'Client/Server PII Redaction & Normalization',
    'Parallel Agent Dispatch (Triage + Log Analysis + Duplicate Detection)',
    'Hybrid RAG Retrieval (Qdrant dense vectors + BM25 sparse exact match)',
    'Root Cause Hypotheses Formulation (LangGraph Orchestration)',
    'Remediation Agent Synthesis (Actionable Fixes with Cited Bug IDs)',
    'Structured Diagnosis Export & Feedback Loop'
  ],
  agents: [
    {
      name: 'Triage Agent',
      role: 'Classification & Completeness Auditor',
      responsibilities: [
        'Determine defect severity (Blocker, Critical, Major, Minor, Trivial)',
        'Assign priority (P1 to P4) and target architectural component',
        'Detect missing reproduction steps or missing environment details'
      ]
    },
    {
      name: 'Log Analysis Agent',
      role: 'Stack Trace & Crash Signature Analyst',
      responsibilities: [
        'Parse stack frames, exceptions, and signal codes',
        'Normalize memory addresses and line offsets for cross-version matching',
        'Construct chronological event timeline leading to failure'
      ]
    },
    {
      name: 'Duplicate Detection Agent',
      role: 'Semantic Similarity & Historical Matcher',
      responsibilities: [
        'Query Qdrant vector database using BAAI/bge-small-en-v1.5 embeddings',
        'Execute BM25 keyword query over normalized exception frames',
        'Fuse rankings using Reciprocal Rank Fusion (RRF) and flag duplicates'
      ]
    },
    {
      name: 'Root Cause Agent',
      role: 'Causal Reasoner & Failure Mechanism Diagnostician',
      responsibilities: [
        'Synthesize outputs from Triage, Log, and Duplicate agents',
        'Formulate ranked root-cause hypotheses with confidence ratings',
        'Ground every deduction in concrete historical bug evidence'
      ]
    },
    {
      name: 'Remediation Agent',
      role: 'Fix Synthesizer & Code Patch Generator',
      responsibilities: [
        'Extract verified code patches from resolved historical defect records',
        'Generate step-by-step remediation plans and rollback precautions',
        'Enforce mandatory citation of historical bug IDs for every claim'
      ]
    }
  ],
  tech_stack: {
    'Frontend': 'React 18 + Vite 6 + TypeScript + Tailwind CSS (iOS System Design)',
    'Backend API': 'Python 3.11 + FastAPI + Pydantic v2',
    'Operational Database': 'PostgreSQL 16 + SQLAlchemy 2 + Alembic',
    'Vector Database': 'Qdrant (HNSW Graph Cosine Metric)',
    'Embeddings': 'BAAI/bge-small-en-v1.5 (384 dimensions, sentence-transformers)',
    'Sparse Search': 'BM25 (rank_bm25 exact token matching)',
    'Agent Orchestrator': 'LangGraph Multi-Agent State Machine',
    'LLM Engine': 'Claude 3.5 Sonnet / Anthropic API (Local Ollama support)',
    'Containerization': 'Docker Compose v2'
  }
};
