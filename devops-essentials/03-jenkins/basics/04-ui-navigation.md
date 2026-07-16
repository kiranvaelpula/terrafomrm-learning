# Jenkins UI Navigation and Features

## Dashboard Overview

The Jenkins dashboard is your central hub for managing jobs, viewing builds, and accessing configuration.

```
┌─────────────────────────────────────────────────────────┐
│ Jenkins  [Search]  [User Menu]  [Notifications]         │
├─────────────────────────────────────────────────────────┤
│ ☰ New Item  People  Build History  Manage Jenkins       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  All      Name              Last Success  Last Failure  │
│  ────────────────────────────────────────────────────   │
│  Status   frontend-build    #42 (2m ago)  #38 (1d ago) │
│  ●●●○○    backend-api       #156 (5m ago) Never        │
│  ●●●●●    deploy-prod       #12 (1h ago)  #10 (1d ago) │
│                                                          │
│  Build Queue               Build Executor Status        │
│  ─────────────────         ─────────────────────────    │
│  (empty)                   Master (2)                   │
│                            ● frontend-build #43          │
│                            ○ (idle)                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Main Navigation Menu

### New Item
Create new jobs, folders, views

**How to Access:** Click "New Item" or `http://jenkins-url/view/all/newJob`

**Quick Actions:**
- Enter item name
- Select project type
- Click OK to configure

### People
View all users and their recent builds

**Useful For:**
- See who triggered builds
- Check individual build history
- User activity tracking

### Build History
Timeline of all builds across all jobs

**Features:**
- Chronological view
- Filter by status
- Search specific builds
- View trends

### Manage Jenkins
System configuration and administration

**Categories:**
1. **System Configuration**
2. **Security**
3. **Status Information**
4. **Troubleshooting**
5. **Tools and Actions**

## Job/Project View

When you click on a job, you see:

```
┌──────────────────────────────────────────────────────┐
│ frontend-build                           [Build Now]  │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Status  [Stage View Graph showing pipeline stages]  │
│                                                       │
│  Permalinks:                                         │
│  • Last build (#43)  • Last stable (#42)            │
│  • Last successful (#42)  • Last failed (#38)        │
│                                                       │
│  Build History          Recent Changes               │
│  #43  (building...)     main: Updated README         │
│  #42  ✓ (5 min)        feat: New feature            │
│  #41  ✓ (2 hr)         fix: Bug fix                 │
│  #40  ✗ (1 day)        test: Added tests            │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### Left Sidebar Options

| Option | Description |
|--------|-------------|
| **Back to Dashboard** | Return to main page |
| **Status** | Current job status |
| **Changes** | SCM changes in builds |
| **Workspace** | Browse job workspace |
| **Build Now** | Trigger immediate build |
| **Configure** | Edit job configuration |
| **Delete Project** | Remove job |
| **Rename** | Change job name |
| **Build with Parameters** | Build with custom params |

## Build View

Click a build number to see details:

```
┌──────────────────────────────────────────────────────┐
│ frontend-build #43                                    │
├──────────────────────────────────────────────────────┤
│  Status: SUCCESS                                      │
│  Duration: 2 min 34 sec                              │
│  Started: 2 minutes ago                              │
│  Finished: 23 seconds ago                            │
│                                                       │
│  Changes:                                             │
│  • john.doe: Updated package dependencies            │
│                                                       │
│  ┌─ Console Output ─────────────────────────────┐   │
│  │ Started by user John Doe                      │   │
│  │ Building in workspace /var/jenkins_home/...  │   │
│  │ [Pipeline] Start of Pipeline                  │   │
│  │ [Pipeline] node                               │   │
│  │ Running on Jenkins in /workspace              │   │
│  │ [Pipeline] {                                  │   │
│  │ [Pipeline] stage                              │   │
│  │ [Pipeline] { (Build)                          │   │
│  │ [Pipeline] echo                               │   │
│  │ Building application...                       │   │
│  │ [Pipeline] }                                  │   │
│  │ [Pipeline] // stage                           │   │
│  │ [Pipeline] End of Pipeline                    │   │
│  │ Finished: SUCCESS                             │   │
│  └────────────────────────────────────────────────┘  │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### Build Detail Options

| Option | Description |
|--------|-------------|
| **Console Output** | Full build logs |
| **Changes** | SCM changes in this build |
| **Tests** | Test results (if available) |
| **Workspaces** | Files in workspace |
| **Artifacts** | Archived files |
| **Pipeline Steps** | Step-by-step execution |
| **Rebuild** | Run again with same params |
| **Replay** | Edit and run pipeline |
| **Delete Build** | Remove build |

## Manage Jenkins Menu

### Configure System

**Path:** Manage Jenkins → Configure System

**Key Sections:**

#### Global Properties
```
Environment variables
Tool locations
Cloud configurations
```

#### Jenkins Location
```
Jenkins URL: http://your-jenkins-url/
System Admin e-mail address: admin@company.com
```

#### # of Executors
```
Number: 2 (for master)
Recommended: 0 (use agents instead)
```

#### Usage
```
○ Use this node as much as possible
● Only build jobs with label restrictions
```

### Configure Global Security

**Path:** Manage Jenkins → Configure Global Security

#### Security Realm
```
● Jenkins' own user database
  ✓ Allow users to sign up
○ LDAP
○ Unix user/group database
○ Delegate to servlet container
```

#### Authorization
```
● Matrix-based security
  User: admin  ✓All ✓Read ✓Configure ✓Build
  User: dev    ✓Read ✓Build
  Anonymous:   ✓Read (jobs only)
```

#### Agent Protocols
```
✓ TCP port for inbound agents
  Fixed: 50000
  Random: (not recommended)
```

#### CSRF Protection
```
✓ Prevent Cross Site Request Forgery exploits
  Crumb Issuer: Default Crumb Issuer
```

### Manage Plugins

**Path:** Manage Jenkins → Manage Plugins

#### Tabs:
- **Updates**: Available plugin updates
- **Available**: New plugins to install
- **Installed**: Currently installed plugins
- **Advanced**: Upload plugin, proxy settings

**Install Plugin:**
1. Go to "Available" tab
2. Search for plugin
3. Check checkbox
4. Click "Install without restart"
5. Or "Download now and install after restart"

**Update Plugin:**
1. Go to "Updates" tab
2. Select plugins
3. Click "Download now and install after restart"

### Global Tool Configuration

**Path:** Manage Jenkins → Global Tool Configuration

#### JDK Installations
```
Name: JDK17
☐ Install automatically
JAVA_HOME: /usr/lib/jvm/java-17-openjdk

[Add JDK button]
```

#### Git
```
Name: Default
Path to Git executable: git

[Add Git button]
```

#### Maven
```
Name: Maven 3.8.6
☐ Install automatically
MAVEN_HOME: /usr/share/maven

[Add Maven button]
```

#### Docker
```
Name: docker
Installation root: /usr/bin/docker

[Add Docker button]
```

### Manage Credentials

**Path:** Manage Jenkins → Manage Credentials → (global) → Add Credentials

#### Username with Password
```
Kind: Username with password
Scope: Global (Jenkins, nodes, items, all child items, etc)
Username: myusername
Password: ••••••••
ID: github-credentials
Description: GitHub access credentials
```

#### SSH Username with private key
```
Kind: SSH Username with private key
Scope: Global
ID: ssh-key-id
Username: git
Private Key: ● Enter directly
              [Text area for key]
Passphrase: (if key is encrypted)
```

#### Secret text
```
Kind: Secret text
Scope: Global
Secret: ••••••••••••••••
ID: api-token
Description: API authentication token
```

### System Information

**Path:** Manage Jenkins → System Information

**Shows:**
- System properties
- Environment variables
- Plugin versions
- Memory usage
- Thread dumps

**Useful for:**
- Debugging environment issues
- Verifying configurations
- Checking available resources

### System Log

**Path:** Manage Jenkins → System Log

**Features:**
- View Jenkins logs
- Filter by log level
- Create custom log recorders
- Troubleshoot issues

**Common Log Recorders:**
```
Name: Git Plugin Debugging
Loggers: 
  - hudson.plugins.git: ALL
  - org.jenkinsci.plugins.gitclient: ALL
```

### Load Statistics

**Path:** Manage Jenkins → Load Statistics

**Graphs:**
- Number of online executors
- Number of busy executors
- Number of available executors
- Queue length

**Use to:**
- Monitor system load
- Identify bottlenecks
- Plan capacity

## Jenkins CLI

Access via command line:

### Download CLI JAR
```bash
# Download
wget http://your-jenkins-url/jnlpJars/jenkins-cli.jar

# Or
curl -O http://your-jenkins-url/jnlpJars/jenkins-cli.jar
```

### Common CLI Commands

```bash
# List jobs
java -jar jenkins-cli.jar -s http://localhost:8080/ \
  -auth admin:password list-jobs

# Build job
java -jar jenkins-cli.jar -s http://localhost:8080/ \
  -auth admin:password build my-job

# Get build status
java -jar jenkins-cli.jar -s http://localhost:8080/ \
  -auth admin:password get-build my-job 42

# Install plugin
java -jar jenkins-cli.jar -s http://localhost:8080/ \
  -auth admin:password install-plugin docker-plugin

# Restart Jenkins
java -jar jenkins-cli.jar -s http://localhost:8080/ \
  -auth admin:password safe-restart
```

## REST API

Jenkins provides extensive REST API:

### Get Job Info
```bash
curl -u admin:password \
  http://localhost:8080/job/my-job/api/json?pretty=true
```

### Trigger Build
```bash
curl -X POST -u admin:password \
  http://localhost:8080/job/my-job/build
```

### Build with Parameters
```bash
curl -X POST -u admin:password \
  http://localhost:8080/job/my-job/buildWithParameters \
  --data "ENVIRONMENT=prod&RUN_TESTS=true"
```

### Get Build Info
```bash
curl -u admin:password \
  http://localhost:8080/job/my-job/42/api/json?pretty=true
```

### Stop Build
```bash
curl -X POST -u admin:password \
  http://localhost:8080/job/my-job/42/stop
```

## Blue Ocean UI

Modern, visual pipeline interface:

**Access:** `http://your-jenkins-url/blue`

**Features:**
- Visual pipeline editor
- Better pipeline visualization
- Improved logs and debugging
- Git integration
- Pull request support

**To Install:**
```
Manage Jenkins → Manage Plugins → Available
Search: Blue Ocean
Install without restart
```

## Views and Organization

### Create Views

**Dashboard → New View**

#### List View
- Shows list of jobs
- Filter by regex, status, name

```
View name: Frontend Jobs
Jobs: 
  ✓ Use a regular expression: frontend-.*
```

#### My View
- Shows jobs you've interacted with

#### Build Pipeline View
- Visualize job dependencies
- Show upstream/downstream

### Folder Organization

```
jenkins/
├── frontend/
│   └── [frontend jobs]
├── backend/
│   └── [backend jobs]
└── infrastructure/
    └── [infrastructure jobs]
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `?` | Show shortcuts help |
| `/` | Focus search box |
| `b` | Build current job |
| `c` | Configure current job |
| `Esc` | Close dialogs |

## Quick Navigation Tips

### 1. Use Search
- Type `/` to focus search
- Search by job name
- Search by build number

### 2. Bookmarks
- Bookmark frequent jobs
- Use permalinks (Last Success, Last Failed)

### 3. Browser Extensions
- Jenkins Notifier
- Jenkins Build Monitor

### 4. RSS Feeds
- Subscribe to job feeds
- Monitor build status

```
http://jenkins-url/job/my-job/rssAll
http://jenkins-url/job/my-job/rssFailed
```

## Mobile Access

Jenkins is responsive and works on mobile:
- View build status
- Check console logs
- Trigger builds (with care!)
- Monitor queue

## Summary

You've mastered Jenkins UI navigation including:
- Dashboard and menu structure
- Job and build views
- Configuration interfaces
- CLI and API access
- Blue Ocean modern UI
- Views and organization

**Pro Tips:**
- Use search frequently
- Master keyboard shortcuts
- Organize with folders/views
- Leverage Blue Ocean for pipelines
- Use API for automation

---

**Previous:** [← First Job](03-first-job.md) | **Next:** [Build Triggers →](05-build-triggers.md)
