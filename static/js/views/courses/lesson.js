Apros.views.CourseLesson = Backbone.View.extend({
  events: {
    'submit .notes-search': 'notesSubmit',
    'input input[type=search]': 'notesSearch',
    'mousedown .notes-resize': 'mousedown',
    'mousemove': 'mousemove',
    'mouseup': 'mouseup',
    'keydown .notes-input': 'saveNote'
  },

  notesSubmit: function(e) {
    e.preventDefault();
  },

  notesSearch: function(e) {
    var el = $(e.currentTarget);
    if (el.val().length > 2) {
      console.log(el.val());
    }
  },

  mousedown: function(e) {
    e.preventDefault();
    this._startY = e.pageY;
    this._startHeight = this.$('.notes-inner').height();
  },

  mousemove: function(e) {
    if (!this._startY) return;
    e.preventDefault();
    var notes = this.$('.notes-inner'),
        newHeight = this._startHeight + (e.pageY - this._startY);
    notes.height(newHeight);
  },

  mouseup: function(e) {
    e.preventDefault();
    delete this._startY;
    delete this._startHeight;
  },

  saveNote: function(e) {
    if (e.which === 13 && !e.shiftKey) {
      e.preventDefault();
      var form = this.$('.notes-entry');
      $.post(form.attr('action'), form.serialize());
    }
  }
});
