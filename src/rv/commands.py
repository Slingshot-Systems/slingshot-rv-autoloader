# rv.commands reference
# https://github.com/AcademySoftwareFoundation/OpenRV/blob/ad0e4d25cbdbc3e9fec98ac46d30d7a3daadd496/src/lib/app/mu_rvui/commands.mud
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    overload,
)

from PySide2.QtCore import QUrl
from PySide2.QtNetwork import QNetworkAccessManager
from PySide2.QtWebEngineWidgets import QWebEnginePage
from PySide2.QtWidgets import QMainWindow, QTabWidget, QToolBar, QWidget

if TYPE_CHECKING:
    from src.rv_schemas.event import Event

# Static Integer Variables
ByteType: int = 6
CDLFileKind: int = 3
CIEXYZ: int = 1
CacheBuffer: int = 1
CacheGreedy: int = 2
CacheOff: int = 0
CheckedMenuState: int = 2
CursorArrow: int = 0
CursorDefault: int = 0
CursorNone: int = 10
DeviceNameID: int = 4
DirectoryFileKind: int = 5
DisabledMenuState: int = -1
EDLFileKind: int = 7
ErrorAlert: int = 2
FloatType: int = 1
HalfType: int = 5
ImageFileKind: int = 1
IndependentDisplayMode: int = 0
InfoAlert: int = 0
IntType: int = 2
LUTFileKind: int = 4
ManyExistingFiles: int = 1
ManyExistingFilesAndDirectories: int = 2
MirrorDisplayMode: int = 1
MixedStateMenuState: int = 3
ModuleNameID: int = 5
MovieFileKind: int = 2
NetworkPermissionAllow: int = 1
NetworkPermissionAsk: int = 0
NetworkPermissionDeny: int = 2
NetworkStatusOff: int = 0
NetworkStatusOn: int = 1
NeutralMenuState: int = 0
NotADisplayMode: int = 2
OneDirectory: int = 4
OneExistingFile: int = 0
OneFileName: int = 3
PlayLoop: int = 0
PlayOnce: int = 1
PlayPingPong: int = 2
RGB709: int = 0
RVFileKind: int = 6
SequenceSession: int = 0
ShortType: int = 7
StackSession: int = 1
StringType: int = 8
UncheckedMenuState: int = 1
UnknownFileKind: int = 0
VideoAndDataFormatID: int = 1
WarningAlert: int = 1


# Type Aliases
Vector2 = Tuple[float, float]
PixelImageInfo = List[Dict[str, Any]]
MenuItem = Dict[str, Any]
SettingsValue = TypeVar(
    "SettingsValue", float, int, str, bool, list[float], list[int], list[str]
)
IOParameter = Dict[str, Any]
IOFormat = Dict[str, Any]
NodeRangeInfo = Dict[str, Any]
RenderedImageInfo = Dict[str, Any]
SourceMediaInfo = Dict[str, Any]
VideoDeviceState = Dict[str, Any]
MetaEvalInfo = Dict[str, Any]
PropertyInfo = Dict[str, Any]


# Function Definitions
def writeNodeDefinition(
    nodeName: str, fileName: str, inlineSourceCode: bool = True
) -> None: ...
def myNetworkHost() -> str: ...
def setPlayMode(mode: int) -> None: ...


def clearSession() -> None: ...


def sourceAtPixel(p: Vector2) -> PixelImageInfo: ...


def getByteProperty(
    propertyName: str, start: int = 0, num: int = 2147483647
) -> List[int]: ...


def isDebug() -> bool: ...


def setRemoteLocalContactName(name: str) -> str: ...


def readProfile(
    fileName: str, node: str, usePath: bool = True, tag: Optional[str] = None
) -> None: ...


def nodeType(nodeName: str) -> str: ...


def setWindowTitle(title: str) -> None: ...


def addSourceMediaRep(
    sourceNode: str,
    mediaRepName: str,
    mediaRepPathsAndOptions: List[str],
    tag: Optional[str] = None,
) -> str: ...


def clearAllButFrame(frame: int) -> None: ...


def imageGeometry(name: str, useStencil: bool = True) -> List[Vector2]: ...


def setViewNode(nodeName: str) -> None: ...


def existingFilesInSequence(sequence: str) -> List[str]: ...


def contractSequences(files: List[str]) -> List[str]: ...


@overload
def relocateSource(sourceNode: str, oldFileName: str, newFileName: str) -> None: ...


@overload
def relocateSource(oldFileName: str, newFileName: str) -> None: ...


def relocateSource(*args, **kwargs) -> None: ...


def nodeExists(nodeName: str) -> bool: ...


def flushCachedNode(nodeName: str, fileDataAlso: bool = False) -> None: ...


def remoteLocalContactName() -> str: ...


def watchFile(filename: str, watch: bool) -> None: ...


def remoteConnections() -> List[str]: ...


def viewSize() -> Vector2: ...


def closestNodesOfType(
    typeName: str, root: Optional[str] = None, depth: int = 0
) -> List[str]: ...


def httpGet(
    url: str,
    headers: List[Tuple[str, str]],
    replyEvent: str,
    authenticationEvent: Optional[str] = None,
    progressEvent: Optional[str] = None,
    ignoreSslErrors: bool = False,
    urlIsEncoded: bool = False,
) -> None: ...


def getApplicationType() -> str: ...


def inc() -> int: ...


def setByteProperty(
    propertyName: str, value: List[int], allowResize: bool = False
) -> None: ...


def getCurrentAttributes() -> List[Tuple[str, str]]: ...


def sourcePixelValue(
    sourceName: str, px: float, py: float
) -> Tuple[float, float, float, float]: ...


def beginCompoundCommand(name: str) -> None: ...


def setCacheMode(mode: int) -> None: ...


def isTopViewToolbarVisible() -> bool: ...


def markedFrames() -> List[int]: ...


def remoteApplications() -> List[str]: ...


def activateMode(name: str) -> None: ...


@overload
def addToSource(sourceNode: str, fileName: str, tag: Optional[str] = None) -> None: ...


@overload
def addToSource(fileName: str, tag: Optional[str] = None) -> None: ...


def addToSource(*args: Any, **kwargs: Any) -> None: ...


def popupMenuAtPoint(x: int, y: int, menu: Optional[List[MenuItem]] = None) -> None: ...


def cacheSize() -> int: ...


def defineMinorMode(
    name: str, sortKey: Optional[str] = None, order: int = 0
) -> None: ...


def scrubAudio(on: bool, chunkDuration: float = 0.0, loopCount: int = 0) -> None: ...


def imageToEventSpace(
    sourceName: str, point: Vector2, normalizedImageOrigin: bool = False
) -> Vector2: ...


def sessionBottomToolBar() -> QToolBar: ...


def isPlaying() -> bool: ...


def getReleaseVariant() -> str: ...


def insertIntProperty(
    propertyName: str, value: List[int], beforeIndex: int = 2147483647
) -> None: ...


def redraw() -> None: ...


def remoteSendMessage(message: str, recipients: Optional[List[str]] = None) -> None: ...


def data() -> Any: ...


def deactivateMode(name: str) -> None: ...


def validateShotgunToken(port: int = -1, tag: Optional[str] = None) -> str: ...


def editProfiles() -> None: ...


def showTopViewToolbar(show: bool) -> None: ...


def undoPathSwapVars(pathWithVars: str) -> str: ...


def remoteDisconnect(remoteContact: str) -> None: ...


def bind(
    modeName: str,
    tableName: str,
    eventName: str,
    func: Any,
    description: Optional[str] = None,
) -> None: ...


def insertHalfProperty(
    propertyName: str, value: list, beforeIndex: int = 2147483647
) -> None: ...


def newImageSourcePixels(
    sourceName: str, frame: int, layer: Optional[str] = None, view: Optional[str] = None
) -> None: ...


def readCDL(filename: str, nodeName: str, activate: bool = False) -> None: ...


def loadChangedFrames(sourceNodes: list) -> None: ...


def openUrl(url: str) -> None: ...


def openMediaFileDialog(
    associated: bool,
    selectType: int,
    filter: Optional[str] = None,
    defaultPath: Optional[str] = None,
    label: Optional[str] = None,
) -> list: ...


def sourceMediaRepsAndNodes(sourceOrSwitchNode: str) -> list[tuple[str, str]]: ...


def undo() -> None: ...


def networkAccessManager() -> QNetworkAccessManager: ...


def remoteNetwork(on: bool) -> None: ...


def isConsoleVisible() -> bool: ...


def addSourceBegin() -> None: ...


def licensingState() -> int: ...


def pushEventTable(table: str) -> None: ...


def getRendererType() -> str: ...


def optionsProgressiveLoading() -> int: ...


def setEventTableBBox(modeName: str, tableName: str, min: list, max: list) -> None: ...


def exportCurrentSourceFrame(filename: str) -> None: ...


def setAudioCacheMode(mode: int) -> None: ...


def rvioSetup() -> None: ...


def sourceMedia(sourceName: str) -> tuple[str, list, list]: ...


def sessionNames() -> list: ...


def javascriptMuExport(frame: QWebEnginePage) -> None: ...


def mainWindowWidget() -> QMainWindow: ...


def getSessionType() -> int: ...


def nodeRangeInfo(nodeName: str) -> NodeRangeInfo: ...


def newSession(files: list) -> None: ...


def existingFramesInSequence(sequence: str) -> list: ...


def hopProfDynName(name: str) -> None: ...


def play() -> None: ...


def sourceGeometry(name: str) -> list: ...


def sourceMediaInfoList(nodeName: str) -> list[SourceMediaInfo]: ...


def setFrameEnd(frame: int) -> None: ...


def isModeActive(name: str) -> bool: ...


def resizeFit() -> None: ...


def mapPropertyToGlobalFrames(
    propName: str, maxDepth: int, root: Optional[str] = None
) -> list: ...


def defineModeMenu(mode: str, menu: list, strict: bool = False) -> None: ...


def nodeImageGeometry(nodeName: str, frame: int) -> Any:  # NodeImageGeometry:
    ...


def stereoSupported() -> bool: ...


def alertPanel(
    associated: bool,
    type: int,
    title: str,
    message: str,
    button0: str,
    button1: str,
    button2: str,
) -> int: ...


def isCurrentFrameError() -> bool: ...


def optionsNoPackages() -> int: ...


def sourceMediaRep(sourceNode: str) -> str: ...


def activeModes() -> list: ...


def setBGMethod(methodName: str) -> None: ...


def filterLiveReviewEvents() -> bool: ...


def addSource(fileNames: list, tag: Optional[str] = None) -> None: ...


def optionsPlay() -> int: ...


def setPresentationMode(value: bool) -> None: ...


def popupMenu(event, menu: Optional[list] = None) -> None: ...


def propertyInfo(propertyName: str) -> PropertyInfo: ...


def ioParameters(
    extension: str, forEncode: bool, codec: Optional[str] = None
) -> list[IOParameter]: ...


def queryDriverAttribute(attribute: str) -> str: ...


def nodesInGroup(nodeName: str) -> list: ...


def sourceNameWithoutFrame(name: str) -> str: ...


def toggleMenuBar() -> None: ...


def sources() -> list: ...


def showBottomViewToolbar(show: bool) -> None: ...


def releaseAllUnusedImages() -> None: ...


def getFloatProperty(
    propertyName: str, start: int = 0, num: int = 2147483647
) -> list: ...


def sourceDataAttributes(
    sourceName: str, mediaName: Optional[str] = None
) -> list[tuple[str, bytes]]: ...


def cacheOutsideRegion() -> bool: ...


def releaseAllCachedImages() -> None: ...


def insertStringProperty(
    propertyName: str, value: list, beforeIndex: int = 2147483647
) -> None: ...


def openUrlFromUrl(url: QUrl) -> None: ...


def getIntProperty(
    propertyName: str, start: int = 0, num: int = 2147483647
) -> list: ...


def theTime() -> float: ...


def getFiltering() -> int: ...


def propertyExists(propertyName: str) -> bool: ...


def sourcesAtFrame(frame: int) -> list: ...


def contentAspect() -> float: ...


def narrowedFrameEnd() -> int: ...


def setCursor(cursorType: int) -> None: ...


def setRendererType(name: str) -> None: ...


def audioCacheInfo() -> tuple: ...


def nextViewNode() -> str: ...


def videoDeviceIDString(moduleName: str, deviceName: str, idtype: int) -> str: ...


def getStringProperty(
    propertyName: str, start: int = 0, num: int = 2147483647
) -> list: ...


def ioFormats() -> list[IOFormat]: ...


def sourceMediaRepSwitchNode(sourceNode: str) -> str: ...


def setRealtime(realtime: bool) -> None: ...


def deleteNode(nodeName: str) -> None: ...


def inputAtPixel(point: list, strict: bool = True) -> str: ...


def insertFloatProperty(
    propertyName: str, value: list, beforeIndex: int = 2147483647
) -> None: ...


def httpPost(
    url: str,
    headers: list[tuple[str, str]],
    postData: bytes,
    replyEvent: str,
    authenticationEvent: Optional[str] = None,
    progressEvent: Optional[str] = None,
    ignoreSslErrors: bool = False,
    urlIsEncoded: bool = False,
) -> None: ...


def setSessionType(sessionType: int) -> None: ...


def presentationMode() -> bool: ...


def myNetworkPort() -> int: ...


def loadTotal() -> int: ...


def optionsPlayReset() -> None: ...


def setRemoteDefaultPermission(permission: int) -> None: ...


def launchTLI() -> None: ...


def eventToImageSpace(
    sourceName: str, point: list[float], normalizedImageOrigin: bool = False
) -> list[float]: ...


def putUrlOnClipboard(url: str, title: str, doEncode: bool = True) -> None: ...


def setSessionFileName(name: str) -> None: ...


def readSettings(
    group: str, name: str, defaultValue: SettingsValue
) -> SettingsValue: ...


def getCurrentImageSize() -> list[float]: ...


def setDriverAttribute(attribute: str, value: str) -> None: ...


def isCaching() -> bool: ...


@overload
def httpPut(
    url: str,
    headers: list[tuple[str, str]],
    putData: bytes,
    replyEvent: str,
    authenticationEvent: str | None = None,
    progressEvent: str | None = None,
    ignoreSslErrors: bool = False,
    urlIsEncoded: bool = False,
) -> None: ...
@overload
def httpPut(
    url: str,
    headers: list[tuple[str, str]],
    putString: str,
    replyEvent: str,
    authenticationEvent: str | None = None,
    progressEvent: str | None = None,
    ignoreSslErrors: bool = False,
    urlIsEncoded: bool = False,
) -> None: ...


def httpPut(*args, **kwargs) -> None: ...


def newNDProperty(
    propertyName: str,
    propertyType: int,
    propertyDimensions: tuple[int, int, int, int],
) -> None: ...


def bindingDocumentation(
    eventName: str, modeName: str | None = None, tableName: str | None = None
) -> str: ...


def setFilterLiveReviewEvents(shouldFilterEvents: bool) -> None: ...


def sourcesRendered() -> list["RenderedImageInfo"]: ...


def redoPathSwapVars(pathWithoutVars: str) -> str: ...


def sourceDisplayChannelNames(sourceName: str) -> list[str]: ...


def isCurrentFrameIncomplete() -> bool: ...


def isRealtime() -> bool: ...


def nodeGroup(nodeName: str) -> str: ...


def setProgressiveSourceLoading(enable: bool) -> None: ...


def sessionFromUrl(url: str) -> None: ...


def nodesOfType(typeName: str) -> list[str]: ...


def logMetrics(event: str) -> None: ...


def isFullScreen() -> bool: ...


def addSourcesVerbose(
    filePathsAndOptions: list[list[str]], tag: str | None = None
) -> None: ...


def setIntProperty(
    propertyName: str, value: list[int], allowResize: bool = False
) -> None: ...


def eval(text: str) -> str: ...


def viewNodes(nodes: list[str]) -> None: ...


def setSourceMedia(
    sourceNode: str, fileNames: list[str], tag: str | None = None
) -> None: ...


def showNetworkDialog() -> None: ...


def getHalfProperty(
    propertyName: str, start: int = 0, num: int = 2147483647
) -> list:  # list[half]:
    ...


def previousViewNode() -> str: ...


def isMarked(frame: int) -> bool: ...


def frameStart() -> int: ...


def updateNodeDefinition(definitionName: str) -> None: ...


def shortAppName() -> str: ...


def prefTabWidget() -> QTabWidget: ...


def setActiveSourceMediaRep(
    sourceNode: str, mediaRepName: str, tag: str | None = None
) -> None: ...


def getCurrentNodesOfType(typeName: str) -> list[str]: ...


def loadCount() -> int: ...


def cacheInfo() -> tuple[int, int, int, float, float, float, list[int]]: ...


def decodePassword(password: str) -> str: ...


def setInc(inc: int) -> None: ...


def sourceMediaInfo(
    sourceName: str, mediaName: str | None = None
) -> "SourceMediaInfo": ...


def fileKind(filename: str) -> int: ...


def startTimer() -> None: ...


def newNode(nodeType: str, nodeName: str | None = None) -> str: ...


def exportCurrentFrame(filename: str) -> None: ...


def playMode() -> int: ...


def metaEvaluateClosestByType(
    frame: int, typeName: str, root: str | None = None, unique: bool = True
) -> list["MetaEvalInfo"]: ...


def redoHistory() -> list[str]: ...


def nodeTypes(userVisibleOnly: bool = False) -> list[str]: ...


def logMetricsWithProperties(event: str, properties: str) -> None: ...


def sourceMediaRepSourceNode(sourceNode: str) -> str: ...


def setFrameStart(frame: int) -> None: ...


def writeProfile(fileName: str, node: str, comments: str | None = None) -> None: ...


def videoState() -> "VideoDeviceState": ...


def unbindRegex(modeName: str, tableName: str, eventName: str) -> None: ...


def saveSession(
    fileName: str, asACopy: bool = False, compressed: bool = False, sparse: bool = False
) -> None: ...


def remoteDefaultPermission() -> int: ...


def bindRegex(
    modeName: str,
    tableName: str,
    eventPattern: str,
    func: Callable[["Event"], None],
    description: str | None = None,
) -> None: ...


def inPoint(frame: int) -> None: ...


def setHalfProperty(
    propertyName: str,
    value: list,  # list[half],
    allowResize: bool = False,
) -> None: ...


def unbind(modeName: str, tableName: str, eventName: str) -> None: ...


def getVersion() -> list[int]: ...


def commandLineFlag(flagName: str, defaultValue: str | None = None) -> str: ...


def metaEvaluate(
    frame: int, root: str | None = None, leaf: str | None = None, unique: bool = True
) -> list["MetaEvalInfo"]: ...


def startupResize(active: bool) -> None: ...


def testNodeInputs(nodeName: str, inputNodes: list[str]) -> None: ...


def activeEventTables() -> list[str]: ...


def endCompoundCommand() -> None: ...


def insertCreatePixelBlock(event: "Event") -> None: ...


def sendInternalEvent(
    eventName: str, contents: str | None = None, senderName: str | None = None
) -> None: ...


def addSourceEnd() -> None: ...


def readLUT(filename: str, nodeName: str, activate: bool = False) -> None: ...


def setFloatProperty(
    propertyName: str, value: list[float], allowResize: bool = False
) -> None: ...


def elapsedTime() -> float: ...


def redo() -> None: ...


def setStringProperty(
    propertyName: str, value: list[str], allowResize: bool = False
) -> None: ...


def properties(nodeName: str) -> list[str]: ...


def setViewSize(width: int, height: int) -> None: ...


def remoteConnect(name: str, host: str, port: int = 0) -> None: ...


def currentFrameStatus() -> int: ...


def bgMethod() -> str: ...


def setFiltering(filterType: int) -> None: ...


@overload
def openFileDialog(
    associated: bool,
    multiple: bool,
    directory: bool,
    filters: list[tuple[str, str]],
    defaultPath: str | None = None,
) -> list[str]: ...


@overload
def openFileDialog(
    associated: bool,
    multiple: bool = False,
    directory: bool = False,
    filter: str | None = None,
    defaultPath: str | None = None,
) -> list[str]: ...


def openFileDialog(*args, **kwargs) -> list[str]:
    """Opens a GUI File Dialog

    Args:
        associated: If true, display as 'sheet' on mac
        multiple: If true, multiple selections are allowed
        directory: If true, only directories allowed
        filter: a string of allowed file extensions in the form "ext1|desc1|ext2|desc2|ext3|desc3|..."
        filters: a list of of allowed file extensions in the form [("ext1", "desc1"), ("ext2", "desc2"), ...]
        defaultPath: the default path to start in
    """
    ...


def imageGeometryByTag(
    name: str, value: str, useStencil: bool = True
) -> list[list[float]]: ...


def sessionName() -> str: ...


def editNodeSource(nodeName: str) -> None: ...


def sessionFileName() -> str: ...


def outPoint(frame: int) -> None: ...


def progressiveSourceLoading() -> bool: ...


def ocioUpdateConfig(node: str | None = None) -> None: ...


def renderedImages() -> list["RenderedImageInfo"]: ...


def sourceAttributes(
    sourceName: str, mediaName: str | None = None
) -> list[tuple[str, str]]: ...


def frame() -> int: ...


def skipped() -> int: ...


def isBuffering() -> bool: ...


def deleteProperty(propertyName: str) -> None: ...


def clearHistory() -> None: ...


def setNodeInputs(nodeName: str, inputNodes: list[str]) -> None: ...


def saveFileDialog(
    associated: bool,
    filter: str | None = None,
    defaultPath: str | None = None,
    directory: bool = False,
) -> str: ...


def setHardwareStereoMode(active: bool) -> None: ...


def narrowedFrameStart() -> int: ...


def writeSettings(group: str, name: str, value: "SettingsValue") -> None: ...


def updateLUT() -> None: ...


def audioTextureComplete(duration: float) -> None: ...


def addSources(
    fileNames: list[str],
    tag: str | None = None,
    processOpts: bool = False,
    merge: bool = False,
) -> None: ...


def setMargins(margins: list[float], allDevices: bool = False) -> None: ...


def isTimerRunning() -> bool: ...


def spoofConnectionStream(
    streamFile: str, timeScale: float, verbose: bool = False
) -> None: ...


def narrowToRange(frameStart: int, frameEnd: int) -> None: ...


def setInPoint(frame: int) -> None: ...


def isMenuBarVisible() -> bool: ...


def newProperty(propertyName: str, propertyType: int, propertyWidth: int) -> None: ...


def imageGeometryByIndex(index: int, useStencil: bool = True) -> list[list[float]]: ...


def resetMbps() -> None: ...


def mbps() -> float: ...


def eventToCameraSpace(sourceName: str, point: list[float]) -> list[float]: ...


def addSourceVerbose(filePathsAndOptions: list[str], tag: str | None = None) -> str: ...


def cacheMode() -> int: ...


def nodeConnections(
    nodeName: str, traverseGroups: bool = False
) -> tuple[list[str], list[str]]: ...


def setOutPoint(frame: int) -> None: ...


def setFPS(fps: float) -> None: ...


def remoteSendEvent(
    event: str, target: str, contents: str, recipients: list[str] | None = None
) -> None: ...


def margins() -> list[float]: ...


def undoHistory() -> list[str]: ...


def stop() -> None: ...


def setFrame(frame: int) -> None: ...


def stopTimer(duration: float) -> None: ...


def markFrame(frame: int, mark: bool) -> None: ...


def isBottomViewToolbarVisible() -> bool: ...


def bindings() -> list[tuple[str, str]]: ...


def encodePassword(password: str) -> str: ...


def writeAllNodeDefinitions(fileName: str, inlineSourceCode: bool = True) -> None: ...


def realFPS() -> float: ...


def audioCacheMode() -> int: ...


def nodes() -> list[str]: ...


@overload
def popEventTable(table: str) -> None: ...


@overload
def popEventTable() -> None: ...


def popEventTable(table: str | None = None) -> None: ...


def viewNode(node: str) -> None: ...


def getCurrentPixelValue(point: list[float]) -> list[float]: ...


def cacheDir() -> str: ...


def audioTextureID() -> int: ...


def close() -> None: ...


def remoteConnectionIsIncoming() -> tuple[bool, str]: ...


def center() -> None: ...


def sequenceOfFile(file: str) -> tuple[str, int]: ...


def frameEnd(frame: int) -> None: ...


def remoteContacts() -> list[str]: ...


def setSessionName(name: str) -> None: ...


def nodeGroupRoot(nodeName: str) -> str: ...


def packageListFromSetting(settingName: str) -> list[str]: ...


def imagesAtPixel(
    point: list[float], tag: str | None = None, sourcesOnly: bool = False
) -> list["PixelImageInfo"]: ...


def crash() -> None: ...


@overload
def reload(startFrame: int, endFrame: int) -> None: ...


@overload
def reload() -> None: ...


def reload(startFrame: int | None = None, endFrame: int | None = None) -> None: ...


def fps() -> float: ...


def sourceMediaReps(sourceNode: str) -> list[str]: ...


def remoteNetworkStatus() -> int: ...


def mainViewWidget() -> QWidget: ...


def setCacheOutsideRegion(cacheOutside: bool) -> None: ...


def remoteSendDataEvent(
    event: str, target: str, interp: str, data: bytes, recipients: list[str]
) -> None: ...


def fullScreenMode(active: bool) -> None: ...


def getCurrentImageChannelNames() -> list[str]: ...


def newImageSource(
    mediaName: str,
    width: int,
    height: int,
    uncropWidth: int,
    uncropHeight: int,
    uncropX: int,
    uncropY: int,
    pixelAspect: float,
    channels: int,
    bitsPerChannel: int,
    floatingPoint: bool,
    startFrame: int,
    endFrame: int,
    fps: float,
    layers: list[str] | None = None,
    views: list[str] | None = None,
) -> None: ...


def showConsole() -> None: ...


def insertByteProperty(
    propertyName: str, value: bytes, beforeIndex: int = 2147483647
) -> None: ...
