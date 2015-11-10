'use strict';

angular.module('oide.filetree', [])

.factory('FiletreeService', ['$http', '$document', '$q', '$log', '$rootScope', function($http,$document,$q,$log, $rootScope) {
  var treeData, selectionDesc;
  treeData = {
    filetreeContents: [
      // { "type": "dir", "filepath": "/tmp/", "filename" : "tmp", "children" : []}
    ]
  };
  selectionDesc = {
    noSelections: true,
    multipleSelections: false,
    dirSelected: false
  };
  var clipboard = [];
  var initializeFiletree = function () {
    $http
      .get('/filebrowser/filetree/a/dir')
      .success(function(data, status, headers, config) {
        for (var i=0;i<data.length;i++) {
          data[i].children = [];
        }
        treeData.filetreeContents = data;
      }).
      error(function(data, status, headers, config) {
        $log.error('Failed to initialize filetree.');
      });
  };
  initializeFiletree();
  var getNodeFromPath = function (filepath, nodeList) {
    var matchedNode;
    for (var i=0;i<nodeList.length;i++) {
      if (filepath.lastIndexOf(nodeList[i].filepath,0) === 0) {
        if (filepath === nodeList[i].filepath) {
          return nodeList[i];
        } else if (nodeList[i].type === 'dir') {
          return getNodeFromPath(filepath, nodeList[i].children);
        }
      }
    }
  };
  var getFilepathsForDir = function (dirpath) {
    var children = getNodeFromPath(dirpath,treeData.filetreeContents).children;
    var filepaths = [];
    for (var i=0;i<children.length;i++) {
      filepaths.push(children[i].filepath);
    }
    return filepaths;
  };
  var removeNodeFromFiletree = function (node){
    var index;
    index = treeData.selectedNodes.indexOf(node);
    if (index >= 0) {
      treeData.selectedNodes.splice(index, 1);
    }
    index = treeData.expandedNodes.indexOf(node);
    if (index >= 0) {
      treeData.expandedNodes.splice(index, 1);
    }
    var filepath, dirpath, parentNode;
    if (node.filepath.slice(-1) === '/') {
      filepath = node.filepath.substring(0,node.filepath.length-1);
    } else {
      filepath = node.filepath;
    }
    dirpath = filepath.substring(0,filepath.lastIndexOf('/')+1);
    parentNode = getNodeFromPath(dirpath,treeData.filetreeContents);
    index = parentNode.children.indexOf(node);
    parentNode.children.splice(index,1);
    describeSelection();
  };
  var isExpanded = function (filepath) {
    for (var i=0;i<treeData.expandedNodes.length;i++) {
      if (treeData.expandedNodes[i].filepath === filepath) {
        return true;
      }
    }
    return false;
  };
  var isDisplayed = function (filepath) {
    for (var i=0;i<treeData.filetreeContents.length;i++) {
      if (treeData.filetreeContents[i].filepath === filepath) {
        return true;
      }
    }
    return false;
  };
  var getDirContents = function (node) {
    $http
      .get('/filebrowser/filetree/a/dir', {
        params: {
          dirpath: node.filepath
        }
      }).
      success(function(data, status, headers, config) {
        var matchedNode;
        var currContents = getFilepathsForDir(node.filepath);
        for (var i=0;i<data.length;i++) {
          if (currContents.indexOf(data[i].filepath) >= 0) {
            matchedNode = getNodeFromPath(data[i].filepath,treeData.filetreeContents);
            if ((data[i].type === 'dir')&&isExpanded(data[i].filepath)) {
              getDirContents(matchedNode);
            }
            currContents.splice(currContents.indexOf(data[i].filepath), 1);
          } else {
            data[i].children = [];
            node.children.push(data[i]);
          }
        }
        var index;
        for (var i=0;i<currContents.length;i++) {
          matchedNode = getNodeFromPath(currContents[i],treeData.filetreeContents);
          removeNodeFromFiletree(matchedNode);
        }
      }).
      error(function(data, status, headers, config) {
        $log.error('Failed to grab dir contents from ',node.filepath);
      });
  };
  var updateFiletree = function () {
    var filepath, node;
    for (var i=0;i<treeData.expandedNodes.length;i++) {
      getDirContents(treeData.expandedNodes[i]);
    }
  };
  var describeSelection = function () {
    selectionDesc.multipleSelections = treeData.selectedNodes.length > 1;
    selectionDesc.noSelections = treeData.selectedNodes.length === 0;
    var dirSelected = false;
    for (var i in treeData.selectedNodes) {
      if (treeData.selectedNodes[i].type==='dir') {
        dirSelected = true;
      }
    }
    selectionDesc.dirSelected = dirSelected;
  };
  return {
    treeData: treeData,
    selectionDesc: selectionDesc,
    clipboardEmpty: function () {
      return clipboard.length === 0;
    },
    describeSelection: function (node, selected) {
      describeSelection();
    },
    getDirContents: function (node) {
      getDirContents(node);
      // updateFiletree();
    },
    updateFiletree: function () {
      updateFiletree();
    },
    openFilesInEditor: function () {
      return treeData.selectedNodes;
    },
    createNewFile: function () {
      var selectedDir = treeData.selectedNodes[0].filepath;
      var newFilePath;
      $http
        .get(
          '/filebrowser/a/fileutil', {
            params: {
              dirpath: selectedDir,
              operation: 'GET_NEXT_UNTITLED_FILE'
            }
        })
        .success(function (data, status, headers, config) {
          $log.debug('GET: ', data);
          newFilePath = data.result;
        })
        .then(function (data, status, headers, config) {
          $http({
            url: '/filebrowser/localfiles'+newFilePath,
            method: 'POST',
            // headers : {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'},
            params: {_xsrf:getCookie('_xsrf')}
            })
            .success(function (data, status, headers, config) {
              $log.debug('POST: ', data);
            })
            .then(function (data, status, headers, config) {
              updateFiletree();
            });
        });
    },
    createNewDir: function () {
      var selectedDir = treeData.selectedNodes[0].filepath;
      var newDirPath;
      $http
        .get(
          '/filebrowser/a/fileutil', {
            params: {
              dirpath: selectedDir,
              operation: 'GET_NEXT_UNTITLED_DIR'
            }
        })
        .success(function (data, status, headers, config) {
          $log.debug('GET: ', data);
          newDirPath = data.result;
        })
        .then(function (data, status, headers, config) {
          $http({
            url: '/filebrowser/localfiles'+newDirPath,
            method: 'POST',
            // headers : {'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'},
            params: {
              _xsrf:getCookie('_xsrf'),
              isDir: true
            }
            })
            .success(function (data, status, headers, config) {
              $log.debug('POST: ', data);
            })
            .then(function (data, status, headers, config) {
              updateFiletree();
            });
        });
    },
    createDuplicate: function () {
      var selectedFile = treeData.selectedNodes[0].filepath;
      var newFilePath;
      $http
        .get(
          '/filebrowser/a/fileutil', {
            params: {
              filepath: selectedFile,
              operation: 'GET_NEXT_DUPLICATE'
            }
        })
        .success(function (data, status, headers, config) {
          $log.debug('GET: ', data);
          newFilePath = data.result;
        })
        .then(function (data, status, headers, config) {
          $http({
            url: '/filebrowser/a/fileutil',
            method: 'POST',
            params: {
              _xsrf:getCookie('_xsrf'),
              operation: 'COPY',
              origpath: selectedFile,
              newpath: newFilePath
            }
            })
            .success(function (data, status, headers, config) {
              $log.debug('Copied: ', data.result);
            })
            .then(function (data, status, headers, config) {
              updateFiletree();
            });
        });
    },
    deleteFiles: function () {
      for (var i=0;i<treeData.selectedNodes.length;i++) {
        var filepath = treeData.selectedNodes[i].filepath;
        $http({
          url: '/filebrowser/localfiles'+filepath,
          method: 'DELETE',
          params: {
            _xsrf:getCookie('_xsrf')
            }
          })
          .success(function (data, status, headers, config) {
            $log.debug('DELETE: ', data.result);
            var node = getNodeFromPath(data.filepath,treeData.filetreeContents);
            removeNodeFromFiletree(node);
            $rootScope.$emit('fileDeleted', data.filepath);
          })
          .then(function (data, status, headers, config) {
            updateFiletree();
          });
      }
    },
    copyFiles: function () {
      clipboard = [];
      var node, i;
      for (i=0;i<treeData.selectedNodes.length;i++) {
        node = treeData.selectedNodes[i]
        clipboard.push({
          'filename': node.filename,
          'filepath': node.filepath
        });
      }
      $log.debug('Copied ', i, ' files to clipboard: ', clipboard)
    },
    pasteFiles: function () {
      var i;
      var newDirPath = treeData.selectedNodes[0].filepath;
      for (i=0;i<clipboard.length;i++) {
        $http({
          url: '/filebrowser/a/fileutil',
          method: 'POST',
          params: {
            _xsrf:getCookie('_xsrf'),
            operation: 'COPY',
            origpath: clipboard[i].filepath,
            newpath: newDirPath+clipboard[i].filename
          }
          })
          .success(function (data, status, headers, config) {
            $log.debug('POST: ', data.result);
          });
      }
      clipboard = [];
      if (!isExpanded(newDirPath)) {
        var node = getNodeFromPath(newDirPath,treeData.filetreeContents);
        treeData.expandedNodes.push(node);
      }
      updateFiletree();
    },
    renameFile: function (newFileName) {
      var node = treeData.selectedNodes[0];
      $http({
        url: '/filebrowser/a/fileutil',
        method: 'POST',
        params: {
          _xsrf:getCookie('_xsrf'),
          operation: 'RENAME',
          filepath: node.filepath,
          newFileName: newFileName
        }
        })
        .success(function (data, status, headers, config) {
          $rootScope.$emit('fileRenamed', node.filepath, data.result);
          removeNodeFromFiletree(node);
          updateFiletree();
          $log.debug('POST: ', data.result);
        });
        // removeNodeFromFiletree(node);
        // updateFiletree();
    }
  };
}]);