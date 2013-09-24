var fileInputWidget = angular.module('fileInputWidgetWithHints', ['ngSanitize']);

// Sets the AngularJS interpolators as <[ and ]>, to not conflict with Django.
fileInputWidget.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('<[');
  $interpolateProvider.endSymbol(']>');
});

function FileReadInputWithHints($scope) {
  $scope.hintPlaceholder = GLOBALS.hintPlaceholder;
  $scope.lowHint = GLOBALS.lowHint;
  $scope.mediumHint = GLOBALS.mediumHint;
  $scope.highHint = GLOBALS.highHint;
  $scope.answer = '';

  $scope.submitAnswer = function(el) {
    var theFile = el.files[0];

    if (theFile.size === 0) {
      alert('Please choose a non-empty file.');
      return;
    }
    if (theFile.size >= 1000) {
      alert('File too large. Please choose a file smaller than 1 kilobyte.');
      return;
    }

    var form = new FormData();
    form.append('file', theFile);

    $('#processing-modal > .modal-body > p').html("Processing uploaded file: " + theFile.name);
    $('#processing-modal').modal('show');

    $.ajax({
      url: '/filereadhandler',
      data: form,
      processData: false,
      contentType: false,
      type: 'POST',
      datatype: 'json',
      success: function(data) {
        console.log(data);
        var answer = data['base64_file_content'];
        if (!answer) {
          alert("An error occurred while processing your input.");
          return;
        }
        if (parent.location.pathname.indexOf('/learn') === 0) {
          window.parent.postMessage(
            JSON.stringify({'submit': answer}),
            window.location.protocol + '//' + window.location.host
          );
        }
      }
    });
  };
}
