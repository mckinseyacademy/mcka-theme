//
// Copyright (C) 2014 edX
//
// Authors:
// Xavier Antoviaque <xavier@antoviaque.org>
//
// This software's license gives you freedom; you can copy, convey,
// propagate, redistribute and/or modify this program under the terms of
// the GNU Affero General Public License (AGPL) as published by the Free
// Software Foundation (FSF), either version 3 of the License, or (at your
// option) any later version of the AGPL published by the FSF.
//
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
// General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program in a file in the toplevel directory called
// "AGPLv3". If not, see <http://www.gnu.org/licenses/>.
//

(function($) {
    if (typeof $.xblock !== "undefined")
        return;

    function getJumpToLink(linkDom) {
        var link_templates = {
            jump_to: /^\/courses\/([^\/]+\/[^\/]+)\/([^\/]+)\/jump_to\/(.+)/,
            jump_to_id: /^\/courses\/([^\/]+\/[^\/]+)\/([^\/]+)\/jump_to_id\/(.+)/
        };
        var link_url = $(linkDom).attr('href');
        for (var jump_type in link_templates) {
            if (!link_templates.hasOwnProperty(jump_type)) continue;
            var template = link_templates[jump_type];
            var match = template.exec(link_url);
            if (match) {
                return {
                    jump_type: jump_type,
                    course_id: match[1],
                    block_type: match[2],
                    block_id: match[3]
                };
            }
        }
    }

    function initArgs(element) {
        var initargs = $(element).find('> .xblock-json-init-args').text();
        return initargs ? JSON.parse(initargs) : {};
    }

    $.xblock = {
        window: window,
        location: location,

        default_options: {
            courseId: null,      // [Mandatory] The course id of the XBlock to display
            usageId: null,       // [Mandatory] The usage id of the XBlock to display
            sessionId: null,     // [Mandatory] User session id from the LMS
            baseDomain: null,    // Common part of the client & LMS domain names
                                 // (eg: `example.com`, defaults to current domain)
            lmsSubDomain: 'lms', // The subdomain part for the LMS (eg, `lms` for `lms.example.com`)
            lmsPort: null,       // Port that LMS API is running on
            lmsSecureURL: false, // Is the LMS on HTTPS?
            useCurrentHost: false, // set to true to load xblock using the current location.hostnam
            viewUrl: null,       // Url of the FragmentView to render
            disableGlobalOptions: false, // set to true to disable the global_options behavior.
            data: {},             // additional data to send to student_view. send as GET parameters
            jumpLinkRewriter: function (jumpToLink) {}, // Function to rewrite jump links if needed for your target platform.
                                                        // See getJumpToLink for details of the object that will be handed to
                                                        // this function.
            block_view: 'student_view'      // block view to load
        },

        global_options: null,

        // JQuery object used to track event listeners. You should use the notify() and listenTo() functions within
        // the runtime object for compatibility with other runtimes that support notifications.
        dispatcher: $({}),

        loadResources: function(resources, options, root) {
            var $this = this,
                numResources = resources.length,
                deferred = $.Deferred(),
                applyResource;

            applyResource = function(index) {
                var hash, resource, head, value, promise;

                if (index >= numResources) {
                    deferred.resolve();
                    return;
                }

                value = resources[index];
                if ($.isArray(value)) {
                    hash = value[0];
                    resource = value[1];
                }
                else{
                    hash = encodeURIComponent(value.data);
                    resource = value
                }
                $this.loadResource(hash, resource, options, root).done(function() {
                    applyResource(index + 1);
                }).fail(function(jqxhr, settings, exception) {
                    deferred.reject();
                });
            };
            applyResource(0);

            return deferred;
        },

        loadResource: function(resource_hash, resource, options, root) {
            var deferred = $.Deferred().resolve(), // By default, don't wait for the resource to load
                resourceURL;

            console.log('Loading XBlock resource', resource_hash, resource);

            if (!this.register_resource_hash(resource_hash, options, root)) {
                console.log('Ignoring already loaded XBlock resource', resource_hash, resource);
                return deferred;
            }

            function getValByIndexOrName(obj, idx, propertyName){
                var val = undefined;
                if (typeof obj !== "undefined" && typeof propertyName !== "undefined") {
                    if ($.isArray(obj)) {
                        val = obj[idx];
                    }
                    else{
                        val = $(obj).prop(propertyName);
                    }
                }
                return val
            }

            var resourceKind = getValByIndexOrName(resource, 0, 'kind');
            var resourceData = getValByIndexOrName(resource, 1, 'data');
            var resourceMimetype = getValByIndexOrName(resource, 2, 'mimetype');

            if (resourceKind === 'url') {
                if (!resourceData.match(/^\/\//) && !resourceData.match(/^(http|https):\/\//)) {
                    resourceURL = this.getLmsBaseURL(options) + resourceData;
                }
                else{
                    resourceURL = resourceData;
                }
                if (resourceMimetype  === 'text/css') {
                    $('head').append('<link href="' + resourceURL + '" rel="stylesheet" />')
                } else if (resourceMimetype === 'application/javascript') {
                    deferred = $.getScript(resourceURL);
                } else {
                    console.log('Unknown XBlock resource mimetype', resourceMimetype);
                }
            } else if (resourceKind === 'text') {
                if (resourceMimetype === 'text/css') {
                    $('head').append('<style type="text/css">' + resourceData + '</style>');
                } else if (resourceMimetype === 'application/javascript') {
                    $.globalEval(resourceData);
                } else if (resourceMimetype === 'text/html') {
                    $('head').append(resourceData);
                } else {
                    console.log('Unknown XBlock resource mimetype', resourceMimetype);
                }
            } else {
                console.log('Unknown XBlock resource kind', resourceKind);
            }
            return deferred;
        },

        register_resource_hash: function(resource_hash, options, root) {
            var loaded_resource_hashes = root.data('loaded_resource_hashes') || [];

            if ($.inArray(resource_hash, loaded_resource_hashes) !== -1) {
                return false;
            }
            loaded_resource_hashes.push(resource_hash);
            return true;
        },

        getRuntime: function(options, root) {
            var $this = this;

            return {
                handlerUrl: function(element, handlerName) {
                    var usageId = $(element).data('usage-id'),
                        courseId = $(element).data('course-id'),
                        lmsBaseURL = $this.getLmsBaseURL(options);

                    if (handlerName=="submit")
                        $this.dispatcher.trigger(handlerName, element);

                    return (lmsBaseURL + '/courses/' + courseId + '/xblock/' + usageId +
                            '/handler/' + handlerName);
                },
                notify: function(name, data) {
                    $this.dispatcher.trigger(name, data);
                },
                listenTo: function(name, callback) {
                    $this.dispatcher.bind(name, callback);
                },
                children: function(element) {
                    return $(element).data('xblock-children');
                },
                childMap: function(block, childName) {
                    var children = this.children(block);
                    for (var i = 0; i < children.length; i++) {
                        var child = children[i];
                        if (child.name == childName) {
                            return child;
                        }
                    }
                }
            };
        },

        initializeXBlocks: function(options, root) {
            // Find and initialize any XBlocks that are descendants of 'root', and their descendants.
            var $this = this;
            return $(root).highestDescendants('.xblock:not(.xblock-initialized)').map(function(idx, blockDOM) {
                return $this.initializeXBlock(options, blockDOM);
            }).toArray();
        },

        initializeXBlock: function(options, blockDOM) {
            var $this = this;
            var $blockDOM = $(blockDOM);
            var blockJS = {};
            // First, initialize any children:
            $blockDOM.data('xblock-children', $this.initializeXBlocks(options, blockDOM));
            // Then initialize this block, if applicable:
            var initFnName = $blockDOM.data('init');
            if (initFnName) {
                // Don't fail when the page still contains XModules
                if (initFnName === 'XBlockToXModuleShim') {
                    console.log('Warning: Unsupported XModule JS init', blockDOM);
                    return;
                }

                if (typeof window[initFnName] != 'function') {
                    console.log('Warning: Undefined init function for XBlock', blockDOM, initFnName);
                    return;
                }

                console.log('Initializing XBlock JS', initFnName, blockDOM);

                var runtime = $this.getRuntime(options, blockDOM);
                var initFn = window[initFnName];
                blockJS = new initFn(runtime, blockDOM, initArgs(blockDOM)) || {};
                blockJS.runtime = runtime;
            }

            blockJS.name = $blockDOM.data('name');
            blockJS.element = blockDOM;
            blockJS.type = $blockDOM.data('block-type');
            $blockDOM.addClass('xblock-initialized');
            $this.dispatcher.trigger("xblock-initialized", $blockDOM);
            return blockJS;
        },

        watchLinks: function(options, root) {
            function jumper(evt) {
                var link_found = getJumpToLink(this);
                if (link_found) {
                    evt.preventDefault();
                    console.log(link_found.course_id, link_found.block_type, link_found.block_id);
                    var link = $(this);
                    link.attr('href', (options.jumpLinkRewriter(link_found) || link.attr('href')));
                }
            }
            root.on('mouseup', 'a', jumper)
        },

        csrfSafeMethod: function(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        },

        setAjaxCSRFToken: function(csrftoken, options, root) {
            var $this = this;

            if (!options.useCurrentHost) {
                $.cookie('csrftoken', csrftoken, $this.getCookieOptions(options));
            }
            $.ajaxSetup({
                xhrFields: {
                    withCredentials: true,
                },
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

                    if (!$this.csrfSafeMethod(settings.type)) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
        },

        getLmsDomain: function(options) {
            if (options.useCurrentHost) {
                if (options.lmsPort && options.lmsPort !== "None") {
                    return this.location.hostname + ':' + options.lmsPort;
                }
                else {
                    return this.location.hostname + ':' + this.location.port;
                }
            }
            else {
                return options.lmsSubDomain + '.' + options.baseDomain;
            }
        },

        getLmsBaseURL: function(options) {
            if (options.lmsSecureURL || 'https:' === document.location.protocol) {
                return 'https://' + this.getLmsDomain(options);
            } else {
                return 'http://' + this.getLmsDomain(options);
            }
        },

        getViewUrl: function(viewName, options) {
            if (options.viewUrl){
                return (this.getLmsBaseURL(options) + options.viewUrl);
            }
            else {
                return (this.getLmsBaseURL(options) + '/courses/' + options.courseId +
                '/xblock/' + options.usageId + '/view/' + viewName);
            }
        },

        getCookieOptions: function(options) {
            var cookieOptions = { domain: '.' + options.baseDomain, path: '/' };

            if (options.lmsSecureURL && 'https:' === document.location.protocol) {
                cookieOptions.secure = true;
            }
            return cookieOptions;
        },

        init: function(options, root) {
            var $this = this,
                deferred = $.Deferred(),
                blockURL = this.getViewUrl(options.block_view, options);

            // Set the LMS session cookie on the shared domain to authenticate on the LMS
            if (!options.sessionId && !options.useCurrentHost) {
                console.log('Error: You must provide a session id from the LMS (cf options)');
                return;
            }

            if (!options.useCurrentHost) {
                $.cookie('sessionid', options.sessionId, $this.getCookieOptions(options));
            }

            // Avoid failing if the XBlock contains XModules
            window.setup_debug = function(){};
            $this.toggleSpinner(root, true);
            var data = options.data;
            if (('bookmarked' in data) === false) {
                data.bookmarked = false;
            }
            if (('username' in data) === false) {
                data.username = 'Anonymous';
            }

            $.ajax({
                url: blockURL,
                dataType: 'json',
                data: data,
                cache: false,
                xhrFields: {
                    withCredentials: true
                },
                statusCode: {
                    404: function() {
                        if(blockURL.match("discussion_board_fragment_view")) {
                            alert(gettext('You are not permitted to view this discussion.'));
                            var discussionHomeUrl = blockURL.split("discussion");
                            window.location.href = discussionHomeUrl[0] + "discussion";
                        }
                    }
                }
            }).done(function(response) {
                if(response.hasOwnProperty('content')) {
                    root.html(response.content);
                }
                else {
                    root.html(response.html);
                }

                $this.loadResources(response.resources, options, root).done(function() {
                    console.log('All XBlock resources successfully loaded');
                    $this.watchLinks(options, root);
                    $this.initializeXBlocks(options, root);
                    deferred.resolve();
                    $this.dispatcher.trigger("xblock-rendered", root);
                });

                $this.setAjaxCSRFToken(response.csrf_token, options, root);
            }).fail(function(response, text_status, error_msg) {
                console.log('Error getting XBlock: ' + text_status);
                console.log('Can be caused by a wrong session id, or missing CORS headers from the LMS');
                deferred.reject();
            });

            return deferred.promise();
        },

        bootstrap: function(options, root) {
            var $this = this;
            options = $.extend({}, this.default_options, options);

            if (!options.baseDomain) {
                options.baseDomain = this.location.host;
            }

            if (!options.disableGlobalOptions) {
                if (this.global_options == null) {
                    this.global_options = {
                        sessionId: options.sessionId,
                        baseDomain: options.baseDomain,
                        lmsSubDomain: options.lmsSubDomain,
                        useCurrentHost: options.useCurrentHost
                    };
                } else {
                    options = $.extend({}, options, this.global_options);
                    console.log('Forcing the use of sessionId: ' + options.sessionId);
                    console.log('Forcing the use of baseDomain: ' + options.baseDomain);
                    console.log('Forcing the use of lmsSubDomain: ' + options.lmsSubDomain);
                    console.log('Forcing the use of useCurrentHost: ' + options.useCurrentHost);
                }
            }

            var initDeferred = this.init(options, root);
            if (typeof initDeferred !== "undefined") {
                initDeferred.always(function () {
                    $this.toggleSpinner(root, false);
                });
            }
            return initDeferred;
        },

        toggleSpinner: function(root, show) {
            var spinner_class = "xblock-spinner";
            if (show) {
                var spinner = $("<div/>").addClass(spinner_class);
                var spinner_styling_wrapper = $("<div/>").addClass("spinner-wrapper").appendTo(spinner);
                spinner_styling_wrapper.append($("<i/>").addClass('fa fa-spin fa-spinner'));
                root.append(spinner);
            } else {
                root.children("."+spinner_class).remove();
            }
        }
    };

    $.fn.xblock = function(options) {
        return this.map(function() {
            return $.xblock.bootstrap(options, $(this));
        });
    };

    // Find all the children of an element that match the selector, but only
    // the first instance found down any path.  For example, we'll find all
    // the ".xblock" elements below us, but not the ones that are themselves
    // contained somewhere inside ".xblock" elements.
    // Code borrowed from edx-platform and edx-sdk
    $.fn.highestDescendants = function(selector) {
        return this.children().map(function(idx, element) {
            if ($(element).is(selector)) {
                return element;
            } else {
                return $(element).highestDescendants(selector).toArray();
            }
        });
    };

})(jQuery);
