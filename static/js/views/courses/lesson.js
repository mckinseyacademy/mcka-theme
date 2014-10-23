Apros.views.CourseLesson = Backbone.View.extend({

  initialize: function() {
    this.listenTo(this.collection, 'add', this.addNote);
  },

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

  addNote: function(note) {
    console.log(note.toJSON());
  },

  saveNote: function(e) {
    if (e.which === 13 && !e.shiftKey) {
      e.preventDefault();
      var _this = this,
          form = this.$('.notes-entry');
      $.post(form.attr('action'), form.serialize())
        .done(function(data){
          var note = new Apros.models.CourseNote(data);
          _this.collection.add(note);
        });
    }
  },

  render: function() {
    this.collection.fetch();
  }
});
