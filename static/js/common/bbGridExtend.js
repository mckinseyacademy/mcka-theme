_.extend(bbGrid.RowView.prototype, {
  render: function () {
    var self = this, isChecked, isDisabled, html,
    cols = _.filter(this.view.colModel, function (col) {return !col.hidden; });
    isChecked = ($.inArray(this.model.id, this.view.selectedRows) >= 0);
    isDisabled = this.model.get('cb_disabled') || false;
    html = this.template({
      isMultiselect: this.view.multiselect,
      isContainSubgrid: this.view.subgrid && this.view.subgridControl,
      isSelected: this.selected || false,
      isChecked: isChecked,
      isDisabled: isDisabled,
      isEscaped: this.view.escape,
      values: _.map(cols, function (col) {
        if (col.actions) {
          col.className = col.name;
          if (_.isFunction(col.actions)) {
            col.value = col.actions.call(self, self.model.id, self.model.attributes, self.view);
          } else {
            col.value = self.view.actions[col.actions].call(self, self.model.id, self.model.attributes, self.view);
          }
        } else {
          col.attributes = _.omit(col, 'name', 'value', 'className', 'title', 'editable', 'width', 'index', 'escape',
          'hidden', 'sorttype', 'filter', 'filterType', 'sortOrder', 'filterColName', 'resizable', 'attributes', 'tooltip');
          col.value = self.getPropByStr(self.model.attributes, col.name);
        }
        return col;
      })
    });
    if (isChecked) {
      this.selected = true;
      this.$el.addClass('warning');
    }
    this.$el.html(html).attr('data-cid', this.model.cid);
    return this;
  }
});
_.extend(bbGrid.TheadView.prototype, {
  template: _.template(
  '<% if (isMultiselect) {%>\
  <th style="width:15px" data-noresize><input type="checkbox"></th>\
  <%} if (isContainSubgrid) {%>\
  <th style="width:15px;" data-noresize/>\
  <%} _.each(cols, function (col) {%>\
  <th <% if (col.tooltip) {%> title="<%=col.tooltip%>" <% } %>\
  <% if (!col.resizable) {%> data-noresize <% } %>\
  <% if (col.width) {%>style="width:<%=col.width%>"<%}%>><%=col.title%><i <% \
  if (col.sortOrder === "asc" ) {%>class="fa fa-chevron-up"<%} else \
  if (col.sortOrder === "desc" ) {%>class="fa fa-chevron-down"<% } %>/></th>\
  <%})%>', null, {
    evaluate: /<%([\s\S]+?)%>/g,
    interpolate: /<%=([\s\S]+?)%>/g,
    escape: /<%-([\s\S]+?)%>/g
  })
});


_.extend(bbGrid.SearchView.prototype, {
  initialize: function (options) {
      _.bindAll(this, 'setSearchOption');
      options.view._collection = options.view.collection;
      this.searchOptionIndex = this.searchOptionIndex || 0;
      this.searchText = '';
  },
  onSearch: function (event) {
      var self = this,
          $el = $(event.target);
      this.searchText = $el.val().trim();
      this.view.collection = this.view._collection;
      if (this.searchText && !this.view.loadDynamic) {
          this.view.setCollection(new this.view._collection.constructor(
              this.view.collection.filter(function (data) {
                  var value = null
                  for (index = 0; index < self.view.colModel.length; index++)
                  {
                    value += data.get(self.view.colModel[index].name);
                  }
                  return ("" + value).toLowerCase().indexOf(self.searchText.toLowerCase()) >= 0;
              })
          ));
      }
      this.view.collection.trigger('reset');
  }
});

_.extend(bbGrid.View.prototype, {
  render: function () {
      if (this.width) {
          this.$el.css('width', this.width);
      }
      if (!this.$grid) {
          this.$grid = $('<table class="bbGrid-grid table table-curved table-condensed" />');
          if (this.caption) {
              this.$grid.append('<caption>' + this.caption + '</caption>');
          }
          this.$grid.appendTo(this.el);
      }
      if (!this.$thead) {
          this.thead = new this.entities.TheadView({view: this});
          this.$thead = this.thead.render();
          this.$grid.append(this.$thead);
      }
      if (!this.$navBar) {
          this.navBar = new this.entities.NavView({view: this});
          this.$navBar = this.navBar.render();
          this.$grid.after(this.$navBar);
          this.$loading = $('<div class="bbGrid-loading progress"><div class="bar bbGrid-loading-progress progress-bar progress-bar-striped active">' + this.dict.loading + '</div></div>');
          this.$navBar.prepend(this.$loading);
      }
      if (!this.$searchBar && this.enableSearch) {
          this.searchBar = new this.entities.SearchView({view: this});
          this.$searchBar = this.searchBar.render();
          //this.$navBar.append(this.$searchBar);
          //this.$searchBar.appendTo(this.el);
          $(this.container.parent()).prepend(this.$searchBar);
      }
      $(this.container).append(this.$el);
      if (!this.autofetch) {
          this.renderPage();
      }
      return this;
  },
  _sortBy: function (models, attributes) {
    var attr, self = this, sortOrder;
    if (attributes.length === 1) {
      attr = attributes[0].name;
      sortOrder = attributes[0].sortOrder;
      models = _.sortBy(models, function (model) {
        var value = model.get(attr)
        if (typeof value == 'string'){
          return value.toLowerCase();
        }
        return value;
      });
      if (sortOrder === 'desc') {
        models.reverse();
      }
      return models;
    } else {
      attr = attributes[0];
      attributes = _.last(attributes, attributes.length - 1);
      models = _.chain(models).sortBy(function (model) {
        var value = model.get(attr)
        if (typeof value == 'string'){
          return value.toLowerCase();
        }
        return value;
      }).groupBy(function (model) {
        var value = model.get(attr)
        if (typeof value == 'string'){
          return value.toLowerCase();
        }
        return value;
      }).toArray().value();
      _.each(models, function (modelSet, index) {
        models[index] = self._sortBy(models[index], attributes, sortOrder);
      });
      return _.flatten(models);
    }
  }
});