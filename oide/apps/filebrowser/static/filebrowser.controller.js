'use strict';

angular.module('oide.filebrowser')
.controller('FilebrowserController', ['FBFiletreeService', '$rootScope', 'FileService', '$scope', 'FilesystemService', function(FiletreeService, $rootScope, FileService, $scope, FilesystemService){
  var self = this;

  $scope.$watch(function(){
      return FileService.getFileData();
    }, function (newValue) {
    self.fileData = newValue;
  });

  $scope.$watch(function(){
      return FileService.getCurrentDirectory();
    }, function (newValue) {
    self.currentDirectory = newValue;
  });

  self.changeDir = function(index) {
    // Form path
    var path = ""
    var i = 0;
    for(var pathComponent in self.currentDirectory) {
      if(self.currentDirectory[pathComponent] != '/')
        path = path + "/" + self.currentDirectory[pathComponent];
      if(i == index) {
        break;
      }
      i++;
    }
    path += "/";
    console.log(path);
    FilesystemService.getFiles({'filepath': path}, function(data, status, headers, config){
      self.fileData = data;
      FileService.setCurrentDirectory(path);
    });
  };

  self.populatePermissions = function() {
    // Perm sting looks like 644, 755 etc
    // Split it into its consituents
    var perm_array = self.selectedFile.perm_string.split('')
    // Permissions object for current file
    self.currentFilePermissions = {
      'user': {
        'r': false,
        'w': false,
        'x': false
      },
      'group': {
        'r': false,
        'w': false,
        'x': false
      },
      'others': {
        'r': false,
        'w': false,
        'x': false
      }
    };

    // TODO: Iterate over object and do in one loop instead of 3

    // User Permissions
    if(perm_array[0] == "7") {
      self.currentFilePermissions['user']['r'] = true;
      self.currentFilePermissions['user']['w'] = true;
      self.currentFilePermissions['user']['x'] = true;
    } else if(perm_array[0] == "6") {
      self.currentFilePermissions['user']['r'] = true;
      self.currentFilePermissions['user']['w'] = true;
    } else if(perm_array[0] == "5") {
      self.currentFilePermissions['user']['r'] = true;
      self.currentFilePermissions['user']['x'] = true;
    } else if(perm_array[0] == "4") {
      self.currentFilePermissions['user']['r'] = true;
    } else if(perm_array[0] == "3") {
      self.currentFilePermissions['user']['w'] = true;
      self.currentFilePermissions['user']['x'] = true;
    } else if(perm_array[0] == "2") {
      self.currentFilePermissions['user']['w'] = true;
    } else if(perm_array[0] == "1") {
      self.currentFilePermissions['user']['x'] = true;
    }

    // Group Permissions
    if(perm_array[1] == "7") {
      self.currentFilePermissions['group']['r'] = true;
      self.currentFilePermissions['group']['w'] = true;
      self.currentFilePermissions['group']['x'] = true;
    } else if(perm_array[1] == "6") {
      self.currentFilePermissions['group']['r'] = true;
      self.currentFilePermissions['group']['w'] = true;
    } else if(perm_array[1] == "5") {
      self.currentFilePermissions['group']['r'] = true;
      self.currentFilePermissions['group']['x'] = true;
    } else if(perm_array[1] == "4") {
      self.currentFilePermissions['group']['r'] = true;
    } else if(perm_array[1] == "3") {
      self.currentFilePermissions['group']['w'] = true;
      self.currentFilePermissions['group']['x'] = true;
    } else if(perm_array[1] == "2") {
      self.currentFilePermissions['group']['w'] = true;
    } else if(perm_array[1] == "1") {
      self.currentFilePermissions['group']['x'] = true;
    }

    // Others Permissions
    if(perm_array[2] == "7") {
      self.currentFilePermissions['others']['r'] = true;
      self.currentFilePermissions['others']['w'] = true;
      self.currentFilePermissions['others']['x'] = true;
    } else if(perm_array[2] == "6") {
      self.currentFilePermissions['others']['r'] = true;
      self.currentFilePermissions['others']['w'] = true;
    } else if(perm_array[2] == "5") {
      self.currentFilePermissions['others']['r'] = true;
      self.currentFilePermissions['others']['x'] = true;
    } else if(perm_array[2] == "4") {
      self.currentFilePermissions['others']['r'] = true;
    } else if(perm_array[2] == "3") {
      self.currentFilePermissions['others']['w'] = true;
      self.currentFilePermissions['others']['x'] = true;
    } else if(perm_array[2] == "2") {
      self.currentFilePermissions['others']['w'] = true;
    } else if(perm_array[2] == "1") {
      self.currentFilePermissions['others']['x'] = true;
    }
  };

  self.show_details = false;
  self.ShowDetails = function(selectedFile){
    self.selectedFile = selectedFile;
    self.show_details = true;
    // Set the permissions for the file
    self.populatePermissions();

  };
}])
.factory('FileService', ['$rootScope', function($rootScope){
  var fileData;
  var currentDirectory = [];
  var setFileData = function(data) {
    fileData = data;
  };

  var getFileData = function(){
    return fileData;
  };

  var getCurrentDirectory = function() {
    return currentDirectory;
  };

  var setCurrentDirectory = function(filepath) {
    currentDirectory = filepath.split("/")
    // Current Directory Path should be '/'
    currentDirectory[0] = "/";
    // Last component will be blank and needs to be spliced
    currentDirectory.splice(-1)
  };

  return {
    setFileData: setFileData,
    getFileData: getFileData,
    setCurrentDirectory: setCurrentDirectory,
    getCurrentDirectory: getCurrentDirectory
  };
}]);
