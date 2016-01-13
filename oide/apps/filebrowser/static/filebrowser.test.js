function getCookie(name) {
  var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
  return r ? r[1] : undefined;
};

describe('Filebrowser', function() {
  var scope;
  var controller;
  beforeEach(module('oide.filebrowser'));
  beforeEach(module('oide.filesystemservice'));

  describe('FilebrowserController Test', function() {
    var httpBackend;
    var http;
    var files;
    var groups = ['saurabh', 'sudo', 'adm'];
    beforeEach(inject(function($controller, $rootScope, $httpBackend, $http, FilesystemService){
      // The injector unwraps the underscores (_) from around the parameter names when matching
      httpBackend = $httpBackend;
      httpBackend.whenGET(/\/filebrowser\/filetree\/a\/dir\?dirpath=.*/).respond(function(){
        return [200, files];
      });
      httpBackend.whenGET('/filebrowser/a/fileutil?operation=GET_GROUPS').respond(function(){
        return [200, groups];
      });
      scope = $rootScope.$new();
      controller = $controller;
      http = $http;

      // Mock FileService
      var currentDirectory = ['/', 'home', 'saurabh'];
      var currentFile = '/home/saurabh/testfile';
      var rootDirectory = '/home/saurabh';
      var volume_info = {
        'percent': '10',
        'used': '10',
        'size': '100'
      };
      files = [{
        "filepath": "/home/saurabh/file1",
        "filename": "file1",
        "group": "saurabh",
        "is_accessible": true,
        "perm": "-rw-rw-r--",
        "perm_string": "664",
        "size": "0.0 KiB",
        "type": "file"
      }, {
        "filepath": "/home/saurabh/file2",
        "filename": "file2",
        "group": "root",
        "is_accessible": false,
        "perm": "-rw-r--r--",
        "perm_string": "644",
        "size": "0.0 KiB",
        "type": "file"
      },
      {
        "filepath": "/home/saurabh/file3",
        "filename": "file3",
        "group": "saurabh",
        "is_accessible": true,
        "perm": "-rw-rw-r--",
        "perm_string": "664",
        "size": "0.0 KiB",
        "type": "file"
      }];
      var fileData;


      mockFileService = {
        getCurrentDirectory: function() {
          return currentDirectory;
        },
        getFileData: function() {
          return currentFile;
        },
        getRootDirectory: function() {
          return rootDirectory;
        },
        getVolumeInfo: function() {
          return volume_info;
        },
        setFileData: function(data) {
          fileData = data;
        },
        getFileData: function(){
          return fileData;
        }
      };

      // Mock FilesystemService
      // mockFilesystemService = {
      //   getGroups: function() {
      //     return groups;
      //   },
      //   getFiles: function() {
      //     http.get('/filebrowser/filetree/a/dir')
      //     .success(function(data){
      //       mockFileService.setFileData(data);
      //     })
      //     .error(function(data){
      //       console.log(data);
      //     });
      //   }
      //
      // };
      mockFilesystemService = FilesystemService;
      // Mock FiletreeService
      mockFiletreeService = {};
      controller = $controller(
        'FilebrowserController as ctrl', {
          $scope: scope,
          FileService: mockFileService,
          FilesystemService: mockFilesystemService,
          FBFiletreeService: mockFiletreeService,
          $modal: {}
        });
        scope.ctrl = controller;
        scope.$apply();
    }));

    it('checks if current directory is set', function() {
      var currentDirectory = mockFileService.getCurrentDirectory();
      var ref = ['/', 'home', 'saurabh'];
      var are_directories_same = is_same(currentDirectory, ref);
      expect(are_directories_same).toBeTruthy();
    });

    it('checks if volume info is set', function(){
      expect(scope.ctrl.volumeUsed).toBe('10');
    });

    it('checks if root directory is set', function(){
      expect(mockFileService.getRootDirectory()).toBe('/home/saurabh')
    });

    function is_same(arr1, arr2) {
      return (arr1.length == arr2.length) && arr1.every(function(element, index){
        return element === arr2[index];
      });
    }

    it('should form a correct current dir path', function(){
      var currentDirectory = scope.ctrl.currentDirectory;
      var ref = ['/', 'home', 'saurabh'];
      var are_directories_same = is_same(currentDirectory, ref);
      expect(are_directories_same).toBeTruthy();
      expect(scope.ctrl.formDirPath()).toBe('/home/saurabh/');
    });

    it('should fetch files for a particular directory', function(){
      mockFilesystemService.getFiles({
        filepath: '/home/saurabh'
      }, function(data){
        // scope.ctrl.fileData = data;
        mockFileService.setFileData(data);
      });
      httpBackend.flush();
      expect(scope.ctrl.fileData).toBeDefined();
      // Length of filedata should be 3
      expect(scope.ctrl.fileData.length).toBe(3);
    });

    it('should show details of an accessible file', function(){
      spyOn(scope.ctrl, 'populatePermissions');
      scope.ctrl.ShowDetails(files[0]);
      // show_details should be set to true
      expect(scope.ctrl.show_details).toBeTruthy();
      // populatePermissions to have been called
      expect(scope.ctrl.populatePermissions).toHaveBeenCalled();
    });

    it('should not show details of an inaccessible file', function(){
      spyOn(scope.ctrl, 'populatePermissions');
      scope.ctrl.ShowDetails(files[1]);
      // show_details should be set to false
      expect(scope.ctrl.show_details).not.toBeTruthy();
      // populatePermissions should not have been called
      expect(scope.ctrl.populatePermissions).not.toHaveBeenCalled();
    });

    it('should populate permissions for the selected file', function(){
      // Set a file as the selected file on the scope
      scope.ctrl.selectedFile = files[0];
      scope.ctrl.populatePermissions();
      // Expect that self.currentFilePermissions would be defined
      expect(scope.ctrl.currentFilePermissions).toBeDefined();
      // Permission should be as expected
      expect(scope.ctrl.currentFilePermissions['user']['r']).toBeTruthy();
      expect(scope.ctrl.currentFilePermissions['user']['w']).toBeTruthy();
      expect(scope.ctrl.currentFilePermissions['user']['x']).not.toBeTruthy();
      expect(scope.ctrl.currentFilePermissions['group']['r']).toBeTruthy();
      expect(scope.ctrl.currentFilePermissions['group']['w']).toBeTruthy();
      expect(scope.ctrl.currentFilePermissions['group']['x']).not.toBeTruthy();
      expect(scope.ctrl.currentFilePermissions['others']['r']).toBeTruthy();
      expect(scope.ctrl.currentFilePermissions['others']['w']).not.toBeTruthy();
      expect(scope.ctrl.currentFilePermissions['others']['x']).not.toBeTruthy();
    });

    it('should refresh the directory', function(){
      // set current directory
      scope.ctrl.currentDirectory = ['/', 'home', 'saurabh'];
      spyOn(mockFilesystemService, 'getFiles');
      scope.ctrl.refreshDirectory();
      httpBackend.flush();
      // Expect the FilesystemService.getFiles method to be called
      expect(mockFilesystemService.getFiles).toHaveBeenCalled();
      // Expect self.fileData to be defined
      expect(scope.ctrl.fileData).toBeDefined();
    });

  });
});
