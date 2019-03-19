_.extend(bbGrid.RowView.prototype, {
  render: function () {
    var self = this, isChecked, isDisabled, html,
    cols = _.filter(this.view.colModel, function (col) {return !col.hidden; });
    isChecked = ($.inArray(this.model.id, this.view.selectedRows) >= 0);
    isDisabled = this.model.get('cb_disabled') || false;
    var _title = ''
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
        if (col.titleAttribute)
        {
            _title = self.getPropByStr(self.model.attributes, col.titleAttribute);
        }
        return col;
      })
    });
    if (isChecked) {
      this.selected = true;
      this.$el.addClass('warning');
    }
    this.$el.html(html).attr('data-cid', this.model.cid);
    if (_title != '')
    {
      this.$el.attr('data-title', _title);
    }
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
  tagName: 'div',
    className: 'bbGrid-search-bar',
    template: _.template(
        '<div class="input-group">\
            <input name="search" class="bbGrid-pager col-md-2 form-control clearable" type="text" placeholder='+'"'+gettext('Search by Keyword')+'"'+'>\
        </div>', null, {
          evaluate: /<%([\s\S]+?)%>/g,
          interpolate: /<%=([\s\S]+?)%>/g,
          escape: /<%-([\s\S]+?)%>/g
        }
  ),
  onSearch: function (event) {
    $(document).trigger('onSearchEvent');
    var self = this;
    $el = $(event.target);
    this.searchText = $el.val().trim();
    this.view.collection = this.view._collection;
    if (this.searchText && !this.view.loadDynamic) {
        this.view.setCollection(new this.view._collection.constructor(
            this.view.collection.filter(function (data) {
                var value = null;
                for (index = 0; index < self.view.colModel.length; index++)
                {
                  value += " " + data.get(self.view.colModel[index].name);
                }
                return (" " + value).toLowerCase().indexOf(self.searchText.toLowerCase()) >= 0;
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
          $(this.container.parent()).prepend(this.$searchBar);
      }
      $(this.container).append(this.$el);
      if (!this.autofetch) {
          this.renderPage();
      }
      updateHeader();
      return this;
  },
  _sortBy: function (models, attributes) {
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
          return sortNumberFixed(valueA,valueB);
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
  },
  rsortBy: function (col) {
    var isSort, sortType, boundComparator;
    isSort = (this.sortName && this.sortName === col.name) ? false : true;
    this.sortName = col.name;
    sortType = col.sorttype || 'string';
    this.sortOrder = (this.sortOrder === 'asc') ? 'desc' : 'asc';
    boundComparator = _.bind(this.stringComparator, this.collection);
    switch (sortType) {
    case 'string':
        boundComparator = _.bind(this.stringComparator, this.collection);
        break;
    case 'number':
        boundComparator = _.bind(this.numberComparator, this.collection);
        break;
    default:
        break;
    }
    if (isSort)
    {
      if(sortType == 'string')
      {
        var _attr = this.sortName;
        this.collection.models = this.collection.models.sort(function (modelA, modelB) {
          var valueA = modelA.get(_attr);
          var valueB = modelB.get(_attr);
          if (typeof valueA == 'string'){
            valueA = valueA.toLowerCase();
          }
          if (typeof valueB == 'string'){
            valueB = valueB.toLowerCase();
          }
          if (typeof valueB == 'string' && typeof valueA == 'string')
            return sortNumberFixed(valueA,valueB);
        });
      }
      else
        this.collection.models = this.collection.sortBy(boundComparator);
    }
    else
    {
      this.collection.models = this.collection.models.reverse();
    }
    updateHeaderOnSort(col);
  },
  renderPage: function (options) {
    options = options || {silent: false};
    var self = this, interval, data;
    if (this.loadDynamic) {
        options.interval = {s: 0, e: this.rows};
        data = {
            page: self.currPage,
            rows: this.rows
        };
        if (this.enableSearch && this.searchBar.searchText) {
            data.search = $.toJSON(this.searchBar.searchText);
            data.searchOption = self.colModel[this.searchBar.searchOptionIndex].name;
        }
        if (!_.isEmpty(this.filterOptions)) {
            data.filter = $.toJSON(this.filterOptions);
        }
        if (this.sortSequence && this.sortSequence.length) {
            data.sort = $.toJSON(this.sortSequence);
        }
        if (!this.autofetch && !options.silent) {
            this.collection.fetch({
                type: 'POST',
                data: data,
                wait: true,
                reset: true,
                silent: true
            });
            return false;
        }
    }
    this.selectedRows = [];
    if (this.onBeforeRender) {
        this.onBeforeRender();
    }
    if (!options.silent) {
        this.thead.render();
    }
    if (this.rows && this.pager) {
        this.pager.render();
    }
    interval = options.interval || this.getIntervalByPage(this.currPage);
    this.showCollection(this.collection.models.slice(interval.s, interval.e));
    if (!this.autofetch && this.collection.length >= 0) {
        this.toggleLoading(false);
    }
    if (this.onReady && !this.autofetch) {
        this.onReady();
    }
    if (this.filterBar && (!options.silent || this.loadDynamic)) {
        this.filterBar.render();
    }
    updateHeader();
  }
});

cloneHeader = function(parentContainer) {

  var clonedHeader = $('.cloned-header');
  if(clonedHeader.length != 0){
    return;
  }

  clonedHeader = $(parentContainer).find('.bbGrid-grid-head').clone(true);
  clonedHeader.attr('data-parent-container', parentContainer);
  clonedHeader.addClass("cloned-header");

  var head = $(parentContainer).find('.bbGrid-grid-head');
  
  if (head.length == 0)
    return;

  var width = window.getComputedStyle(head[0]).width;
  var height = window.getComputedStyle(head[0]).height;
  clonedHeader.css({"width": width, "height": height});
  head.css("height", parseFloat(height) + 15);

  var tr = $(parentContainer).find('.bbGrid-grid').find('.bbGrid-grid-head').find('tr');
  var trwidth = window.getComputedStyle(tr[0]).width;
  var trheight = window.getComputedStyle(tr[0]).height;
  clonedHeader.find('tr').css({"width": trwidth, "height": trheight});
  tr.css("height", 'inherit');

  var thWidths = []
  var thHeights = []
  $(parentContainer).find('.bbGrid-grid').find('.bbGrid-grid-head').find('th').each(function(index, value){
    var width = window.getComputedStyle(value).width;
    var height = window.getComputedStyle(value).height;
    thWidths.push(width);
    thHeights.push(height);
  });
  var i = 0
  clonedHeader.find('th').each(function(index, value){
    $(value).css({"width": thWidths[i], "height": thHeights[i]});
    i = i+1;
  });

  $(parentContainer).prepend('<div class="clonedHeaderContainer"></div>');
  var clonedHeaderContainer = $('.clonedHeaderContainer');
  clonedHeaderContainer.append(clonedHeader);
  clonedHeaderContainer.css("height", parseFloat(height) + 15);
  var pos = head.position();
  clonedHeaderContainer.css('left', pos.left);
  var containerWidth = window.getComputedStyle(clonedHeaderContainer[0]).width;
  var bbGridContainer = $(parentContainer).find('.bbGrid-container');
  var bbGridContainerWidth = window.getComputedStyle(bbGridContainer[0]).width;
  clonedHeaderContainer.css("width", parseFloat(bbGridContainerWidth));
  if(window.getComputedStyle(clonedHeaderContainer[0]).width < window.getComputedStyle(clonedHeader[0]).width)
  {
    clonedHeaderContainer.css("width", parseFloat(bbGridContainerWidth) - 15);
  }

  clonedHeaderContainer.on('scroll', function(event){
    var left = $(this).scrollLeft();
    $('.bbGrid-container').scrollLeft(left);
  });

  $('.bbGrid-container').on('scroll', function(event){
    var left = $(this).scrollLeft();
    $('.clonedHeaderContainer').scrollLeft(left);
  });
}

updateHeader = function() {

  var clonedHeader = $('.cloned-header');
  if(clonedHeader.length == 0){
    return;
  }
  if(!(jQuery.isEmptyObject(clonedHeader))){
    var parentContainer = clonedHeader.attr('data-parent-container');
    var head = $(parentContainer).find('.bbGrid-grid').find('.bbGrid-grid-head')[0];
    var width = window.getComputedStyle(head).width;
    var height = window.getComputedStyle(head).height;
    clonedHeader.css({"width": width, "height": height});
    var clonedHeaderContainer = $('.clonedHeaderContainer');
    var bbGridContainer = $(parentContainer).find('.bbGrid-container');
    var bbGridContainerWidth = window.getComputedStyle(bbGridContainer[0]).width;
    clonedHeaderContainer.css("width", parseFloat(bbGridContainerWidth));
    if(window.getComputedStyle(clonedHeaderContainer[0]).width < window.getComputedStyle(clonedHeader[0]).width)
    {
      clonedHeaderContainer.css("width", parseFloat(bbGridContainerWidth) - 15);
    }
    var parent = $(bbGridContainer).parent();
    var left = window.getComputedStyle(bbGridContainer[0]).left - window.getComputedStyle(parent[0]).left;
    clonedHeaderContainer.css('left', parseFloat(left));
    
    var tr = $(parentContainer).find('.bbGrid-grid').find('.bbGrid-grid-head').find('tr')[0];
    var trwidth = window.getComputedStyle(tr).width;
    var trheight = window.getComputedStyle(tr).height;
    clonedHeader.find('tr').css({"width": trwidth, "height": trheight});

    var thWidths = []
    var thHeights = []
    $(parentContainer).find('.bbGrid-grid').find('.bbGrid-grid-head').find('th').each(function(index, value){
      var width = window.getComputedStyle(value).width;
      var height = window.getComputedStyle(value).height;
      thWidths.push(width);
      thHeights.push(height);
    });
    var i = 0
    clonedHeader.find('th').each(function(index, value){
      $(value).css({"width": thWidths[i], "height": thHeights[i]});
      i = i+1;
    });
  }
}

updateHeaderOnSort = function(col) {

  var clonedHeader = $('.cloned-header');
  var parentContainer = clonedHeader.attr('data-parent-container');
  $(parentContainer).find('.cloned-header').find('th').each(function(index, value){
    var text = $(value).text();
    var tag = $(value).find('i');
    if(text == col.title){
      if(col.sortOrder === "asc" ){
        tag.removeClass("fa fa-chevron-down");
        tag.addClass("fa fa-chevron-up");
      } else if(col.sortOrder === "desc" ){
        tag.removeClass("fa fa-chevron-up");
        tag.addClass("fa fa-chevron-down");
      }
    } else {
      tag.removeClass("fa fa-chevron-up fa-chevron-down");
    }
  });
}

function sortNumberFixed(elementA, elementB) {
    var n;
    var elementAsplit = elementA.match(/([^0-9]+)|([0-9]+)/g);
    for (var j in elementAsplit) {
      if( ! isNaN(n = parseInt(elementAsplit[j])) ){
        elementAsplit[j] = n;
      }
    }
    var elementBsplit = elementB.match(/([^0-9]+)|([0-9]+)/g);
    for (var j in elementBsplit) {
      if( ! isNaN(n = parseInt(elementBsplit[j])) ){
        elementBsplit[j] = n;
      }
    }
    for (var i in elementAsplit) {
      if (elementBsplit.length < i || elementAsplit[i] < elementBsplit[i]) {
        return -1; // x is longer
      }
      if (elementAsplit[i] > elementBsplit[i]) {
        return 1;
      }
    }
    return 0;
}