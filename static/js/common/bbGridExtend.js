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

_.extend(bbGrid.View.prototype, {
  _sortBy: function (models, attributes) {
    console.log('sorting');
    var attr, self = this, sortOrder;
    if (attributes.length === 1) {
      attr = attributes[0].name;
      sortOrder = attributes[0].sortOrder;
      models = models.sort(function (modelA, modelB) {
        var valueA = modelA.get(attr);
        var valueB = modelB.get(attr);
        if (typeof valueA == 'string'){
          valueA = valueA.toLowerCase();
        }
        if (typeof valueB == 'string'){
          valueB = valueB.toLowerCase();
        }
        if (typeof valueB == 'string' && typeof valueA == 'string')
          return valueA.localeCompare(valueB);
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