// jquery.tweet.js - See http://tweet.seaofclouds.com/ or https://github.com/seaofclouds/tweet for more info
// Copyright (c) 2008-2012 Todd Matthews & Steve Purcell
(function (factory) {
  if (typeof define === 'function' && define.amd)
    define(['jquery'], factory); // AMD support for RequireJS etc.
  else
    factory(jQuery);
}(function ($) {
  $.fn.tweet = function(o){
    var s = $.extend({
      username: null,                           // [string or array] required unless using the 'query' option; one or more twitter screen names (use 'list' option for multiple names, where possible)
      list: null,                               // [string]   optional name of list belonging to username
      favorites: false,                         // [boolean]  display the user's favorites instead of his tweets
      query: null,                              // [string]   optional search query (see also: http://search.twitter.com/operators)
      avatar_size: null,                        // [integer]  height and width of avatar if displayed (48px max)
      count: 3,                                 // [integer]  how many tweets to display?
      fetch: null,                              // [integer]  how many tweets to fetch via the API (set this higher than 'count' if using the 'filter' option)
      page: 1,                                  // [integer]  which page of results to fetch (if count != fetch, you'll get unexpected results)
      retweets: true,                           // [boolean]  whether to fetch (official) retweets (not supported in all display modes)
      intro_text: null,                         // [string]   do you want text BEFORE your your tweets?
      outro_text: null,                         // [string]   do you want text AFTER your tweets?
      join_text:  null,                         // [string]   optional text in between date and tweet, try setting to "auto"
      auto_join_text_default: " I said, ",      // [string]   auto text for non verb: "I said" bullocks
      auto_join_text_ed: " I ",                 // [string]   auto text for past tense: "I" surfed
      auto_join_text_ing: " I am ",             // [string]   auto tense for present tense: "I was" surfing
      auto_join_text_reply: " I replied to ",   // [string]   auto tense for replies: "I replied to" @someone "with"
      auto_join_text_url: " I was looking at ", // [string]   auto tense for urls: "I was looking at" http:...
      loading_text: null,                       // [string]   optional loading text, displayed while tweets load
      refresh_interval: null,                   // [integer]  optional number of seconds after which to reload tweets
      twitter_url: "twitter.com",               // [string]   custom twitter url, if any (apigee, etc.)
      twitter_api_url: "api.twitter.com",       // [string]   custom twitter api url, if any (apigee, etc.)
      twitter_search_url: "search.twitter.com", // [string]   custom twitter search url, if any (apigee, etc.)
      template: "{avatar}{time}{join} {text}",  // [string or function] template used to construct each tweet <li> - see code for available vars
      comparator: function(tweet1, tweet2) {    // [function] comparator used to sort tweets (see Array.sort)
        return tweet2["tweet_time"] - tweet1["tweet_time"];
      },
      filter: function(tweet) {                 // [function] whether or not to include a particular tweet (be sure to also set 'fetch')
        return true;
      }
      // You can attach callbacks to the following events using jQuery's standard .bind() mechanism:
      //   "loaded" -- triggered when tweets have been fetched and rendered
    }, o);

    // See http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    var url_regexp = /\b((?:https?:\/\/|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))/gi;

    // Expand values inside simple string templates with {placeholders}
    function t(template, info) {
      if (typeof template === "string") {
        var result = template;
        for(var key in info) {
          var val = info[key];
          result = result.split('{'+key+'}').join(val === null ? '' : val);
        }
        return result;
      } else return template(info);
    }
    // Export the t function for use when passing a function as the 'template' option
    $.extend({tweet: {t: t}});

    function replacer (regex, replacement) {
      return function() {
        var returning = [];
        this.each(function() {
          returning.push(this.replace(regex, replacement));
        });
        return $(returning);
      };
    }

    function escapeHTML(s) {
      return s.replace(/</g,"&lt;").replace(/>/g,"^&gt;");
    }

    $.fn.extend({
      linkUser: replacer(/(^|[\W])@(\w+)/gi, "$1<span class=\"at\">@</span><a href=\"http://"+s.twitter_url+"/$2\">$2</a>"),
      // Support various latin1 (\u00**) and arabic (\u06**) alphanumeric chars
      linkHash: replacer(/(?:^| )[\#]+([\w\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff\u0600-\u06ff]+)/gi,
                         ' <a href="http://'+s.twitter_search_url+'/search?q=&tag=$1&lang=all'+
                         ((s.username && s.username.length == 1 && !s.list) ? '&from='+s.username.join("%2BOR%2B") : '')+
                         '" class="tweet_hashtag">#$1</a>'),
      makeHeart: replacer(/(&lt;)+[3]/gi, "<tt class='heart'>&#x2665;</tt>")
    });

    function linkURLs(text, entities) {
      return text.replace(url_regexp, function(match) {
        var url = (/^[a-z]+:/i).test(match) ? match : "http://"+match;
        var text = match;
        for(var i = 0; i < entities.length; ++i) {
          var entity = entities[i];
          if (entity.url == url && entity.expanded_url) {
            url = entity.expanded_url;
            text = entity.display_url;
            break;
          }
        }
        return "<a href=\""+escapeHTML(url)+"\">"+escapeHTML(text)+"</a>";
      });
    }

    function parse_date(date_str) {
      // The non-search twitter APIs return inconsistently-formatted dates, which Date.parse
      // cannot handle in IE. We therefore perform the following transformation:
      // "Wed Apr 29 08:53:31 +0000 2009" => "Wed, Apr 29 2009 08:53:31 +0000"
      return Date.parse(date_str.replace(/^([a-z]{3})( [a-z]{3} \d\d?)(.*)( \d{4})$/i, '$1,$2$4$3'));
    }

    function extract_relative_time(date) {
      var toInt = function(val) { return parseInt(val, 10); };
      var relative_to = new Date();
      var delta = toInt((relative_to.getTime() - date) / 1000);
      if (delta < 1) delta = 0;
      return {
        days:    toInt(delta / 86400),
        hours:   toInt(delta / 3600),
        minutes: toInt(delta / 60),
        seconds: toInt(delta)
      };
    }

    function format_relative_time(time_ago) {
      if ( time_ago.days > 2 )     return 'about ' + time_ago.days + ' days ago';
      if ( time_ago.hours > 24 )   return 'about a day ago';
      if ( time_ago.hours > 2 )    return 'about ' + time_ago.hours + ' hours ago';
      if ( time_ago.minutes > 45 ) return 'about an hour ago';
      if ( time_ago.minutes > 2 )  return 'about ' + time_ago.minutes + ' minutes ago';
      if ( time_ago.seconds > 1 )  return 'about ' + time_ago.seconds + ' seconds ago';
      return 'just now';
    }

    function build_auto_join_text(text) {
      if (text.match(/^(@([A-Za-z0-9-_]+)) .*/i)) {
        return s.auto_join_text_reply;
      } else if (text.match(url_regexp)) {
        return s.auto_join_text_url;
      } else if (text.match(/^((\w+ed)|just) .*/im)) {
        return s.auto_join_text_ed;
      } else if (text.match(/^(\w*ing) .*/i)) {
        return s.auto_join_text_ing;
      } else {
        return s.auto_join_text_default;
      }
    }

    function build_api_url() {
      var proto = ('https:' == document.location.protocol ? 'https:' : 'http:');
      var count = (s.fetch === null) ? s.count : s.fetch;
      var common_params = '&include_entities=1&callback=?';
      if (s.list) {
        return proto+"//"+s.twitter_api_url+"/1/"+s.username[0]+"/lists/"+s.list+"/statuses.json?page="+s.page+"&per_page="+count+common_params;
      } else if (s.favorites) {
        return proto+"//"+s.twitter_api_url+"/1/favorites.json?screen_name="+s.username[0]+"&page="+s.page+"&count="+count+common_params;
      } else if (s.query === null && s.username.length == 1) {
        return proto+'//'+s.twitter_api_url+'/1/statuses/user_timeline.json?screen_name='+s.username[0]+'&count='+count+(s.retweets ? '&include_rts=1' : '')+'&page='+s.page+common_params;
      } else {
        var query = (s.query || 'from:'+s.username.join(' OR from:'));
        return proto+'//'+s.twitter_search_url+'/search.json?&q='+encodeURIComponent(query)+'&rpp='+count+'&page='+s.page+common_params;
      }
    }

    function extract_avatar_url(item, secure) {
      if (secure) {
        return ('user' in item) ?
          item.user.profile_image_url_https :
          extract_avatar_url(item, false).
            replace(/^http:\/\/[a-z0-9]{1,3}\.twimg\.com\//, "https://s3.amazonaws.com/twitter_production/");
      } else {
        return item.profile_image_url || item.user.profile_image_url;
      }
    }

    // Convert twitter API objects into data available for
    // constructing each tweet <li> using a template
    function extract_template_data(item){
      var o = {};
      o.item = item;
      o.source = item.source;
      o.screen_name = item.from_user || item.user.screen_name;
      // The actual user name is not returned by all Twitter APIs, so please do not
      // file an issue if it is empty:
      o.name = item.from_user_name || item.user.name;
      o.retweet = typeof(item.retweeted_status) != 'undefined';

      o.tweet_time = parse_date(item.created_at);
      o.join_text = s.join_text == "auto" ? build_auto_join_text(item.text) : s.join_text;
      o.tweet_id = item.id_str;
      o.twitter_base = "http://"+s.twitter_url+"/";
      o.user_url = o.twitter_base+o.screen_name;
      o.tweet_url = o.user_url+"/status/"+o.tweet_id;
      o.reply_url = o.twitter_base+"intent/tweet?in_reply_to="+o.tweet_id;
      o.retweet_url = o.twitter_base+"intent/retweet?tweet_id="+o.tweet_id;
      o.favorite_url = o.twitter_base+"intent/favorite?tweet_id="+o.tweet_id;
      o.retweeted_screen_name = o.retweet && item.retweeted_status.user.screen_name;
      o.tweet_relative_time = format_relative_time(extract_relative_time(o.tweet_time));
      o.entities = item.entities ? (item.entities.urls || []).concat(item.entities.media || []) : [];
      o.tweet_raw_text = o.retweet ? ('RT @'+o.retweeted_screen_name+' '+item.retweeted_status.text) : item.text; // avoid '...' in long retweets
      o.tweet_text = $([linkURLs(o.tweet_raw_text, o.entities)]).linkUser().linkHash()[0];
      o.retweeted_tweet_text = $([linkURLs(item.text, o.entities)]).linkUser().linkHash()[0];
      o.tweet_text_fancy = $([o.tweet_text]).makeHeart()[0];

      o.avatar_size = s.avatar_size;
      o.avatar_url = extract_avatar_url(o.retweet ? item.retweeted_status : item, (document.location.protocol === 'https:'));
      o.avatar_screen_name = o.retweet ? o.retweeted_screen_name : o.screen_name;
      o.avatar_profile_url = o.twitter_base+o.avatar_screen_name;

      // Default spans, and pre-formatted blocks for common layouts
      o.user = t('<a class="tweet_user" href="{user_url}">{screen_name}</a>', o);
      o.join = s.join_text ? t('<span class="tweet_join">{join_text}</span>', o) : '';
      o.avatar = o.avatar_size ?
        t('<a class="tweet_avatar" href="{avatar_profile_url}"><img src="{avatar_url}" height="{avatar_size}" width="{avatar_size}" alt="{avatar_screen_name}\'s avatar" title="{avatar_screen_name}\'s avatar" border="0"/></a>', o) : '';
      o.time = t('<span class="tweet_time"><a href="{tweet_url}" title="view tweet on twitter">{tweet_relative_time}</a></span>', o);
      o.text = t('<span class="tweet_text">{tweet_text_fancy}</span>', o);
      o.retweeted_text = t('<span class="tweet_text">{retweeted_tweet_text}</span>', o);
      o.reply_action = t('<a class="tweet_action tweet_reply" href="{reply_url}">reply</a>', o);
      o.retweet_action = t('<a class="tweet_action tweet_retweet" href="{retweet_url}">retweet</a>', o);
      o.favorite_action = t('<a class="tweet_action tweet_favorite" href="{favorite_url}">favorite</a>', o);
      return o;
    }

    function render_tweets(widget, tweets) {
      var list = $('<ul class="tweet_list">');
      list.append($.map(tweets, function(o) { return "<li>" + t(s.template, o) + "</li>"; }).join('')).
        children('li:first').addClass('tweet_first').end().
        children('li:odd').addClass('tweet_even').end().
        children('li:even').addClass('tweet_odd');

      $(widget).empty().append(list);
      if (s.intro_text) list.before('<p class="tweet_intro">'+s.intro_text+'</p>');
      if (s.outro_text) list.after('<p class="tweet_outro">'+s.outro_text+'</p>');

      $(widget).trigger("loaded").trigger((tweets.length === 0 ? "empty" : "full"));
      if (s.refresh_interval) {
        window.setTimeout(function() { $(widget).trigger("tweet:load"); }, 1000 * s.refresh_interval);
      }
    }

    function load(widget) {
      var loading = $('<p class="loading">'+s.loading_text+'</p>');
      if (s.loading_text) $(widget).not(":has(.tweet_list)").empty().append(loading);
      $.getJSON(build_api_url(), function(data){
        var tweets = $.map(data.results || data, extract_template_data);
        tweets = $.grep(tweets, s.filter).sort(s.comparator).slice(0, s.count);
        $(widget).trigger("tweet:retrieved", [tweets]);
      });
    }

    return this.each(function(i, widget){
      if(s.username && typeof(s.username) == "string"){
        s.username = [s.username];
      }

      $(widget).unbind("tweet:render").unbind("tweet:retrieved").unbind("tweet:load").
        bind({
          "tweet:load": function() { load(widget); },
          "tweet:retrieved": function(ev, tweets) {
            $(widget).trigger("tweet:render", [tweets])
          },
          "tweet:render": function(ev, tweets) {
            render_tweets($(widget), tweets);
          }
        }).trigger("tweet:load");
    });
  };
}));

;(function($, window, document, undefined) {

	var pluginName = 'stellar',
		defaults = {
			scrollProperty: 'scroll',
			positionProperty: 'position',
			horizontalScrolling: false,
			verticalScrolling: true,
			horizontalOffset: 0,
			verticalOffset: 0,
			responsive: true,
			parallaxBackgrounds: true,
			parallaxElements: true,
			hideDistantElements: true,
			hideElement: function($elem) { $elem.hide(); },
			showElement: function($elem) { $elem.show(); }
		},

		scrollProperty = {
			scroll: {
				getLeft: function($elem) { return $elem.scrollLeft(); },
				setLeft: function($elem, val) { $elem.scrollLeft(val); },

				getTop: function($elem) { return $elem.scrollTop();	},
				setTop: function($elem, val) { $elem.scrollTop(val); }
			},
			position: {
				getLeft: function($elem) { return parseInt($elem.css('left'), 10) * -1; },
				getTop: function($elem) { return parseInt($elem.css('top'), 10) * -1; }
			},
			margin: {
				getLeft: function($elem) { return parseInt($elem.css('margin-left'), 10) * -1; },
				getTop: function($elem) { return parseInt($elem.css('margin-top'), 10) * -1; }
			},
			transform: {
				getLeft: function($elem) {
					var computedTransform = getComputedStyle($elem[0])[prefixedTransform];
					return (computedTransform !== 'none' ? parseInt(computedTransform.match(/(-?[0-9]+)/g)[4], 10) * -1 : 0);
				},
				getTop: function($elem) {
					var computedTransform = getComputedStyle($elem[0])[prefixedTransform];
					return (computedTransform !== 'none' ? parseInt(computedTransform.match(/(-?[0-9]+)/g)[5], 10) * -1 : 0);
				}
			}
		},

		positionProperty = {
			position: {
				setLeft: function($elem, left) { $elem.css('left', left); },
				setTop: function($elem, top) { $elem.css('top', top); }
			},
			transform: {
				setPosition: function($elem, left, startingLeft, top, startingTop) {
					$elem[0].style[prefixedTransform] = 'translate3d(' + (left - startingLeft) + 'px, ' + (top - startingTop) + 'px, 0)';
				}
			}
		},

		// Returns a function which adds a vendor prefix to any CSS property name
		vendorPrefix = (function() {
			var prefixes = /^(Moz|Webkit|Khtml|O|ms|Icab)(?=[A-Z])/,
				style = $('script')[0].style,
				prefix = '',
				prop;

			for (prop in style) {
				if (prefixes.test(prop)) {
					prefix = prop.match(prefixes)[0];
					break;
				}
			}

			if ('WebkitOpacity' in style) { prefix = 'Webkit'; }
			if ('KhtmlOpacity' in style) { prefix = 'Khtml'; }

			return function(property) {
				return prefix + (prefix.length > 0 ? property.charAt(0).toUpperCase() + property.slice(1) : property);
			};
		}()),

		prefixedTransform = vendorPrefix('transform'),

		supportsBackgroundPositionXY = $('<div />', { style: 'background:#fff' }).css('background-position-x') !== undefined,

		setBackgroundPosition = (supportsBackgroundPositionXY ?
			function($elem, x, y) {
				$elem.css({
					'background-position-x': x,
					'background-position-y': y
				});
			} :
			function($elem, x, y) {
				$elem.css('background-position', x + ' ' + y);
			}
		),

		getBackgroundPosition = (supportsBackgroundPositionXY ?
			function($elem) {
				return [
					$elem.css('background-position-x'),
					$elem.css('background-position-y')
				];
			} :
			function($elem) {
				return $elem.css('background-position').split(' ');
			}
		),

		requestAnimFrame = (
			window.requestAnimationFrame       ||
			window.webkitRequestAnimationFrame ||
			window.mozRequestAnimationFrame    ||
			window.oRequestAnimationFrame      ||
			window.msRequestAnimationFrame     ||
			function(callback) {
				setTimeout(callback, 1000 / 60);
			}
		);

	function Plugin(element, options) {
		this.element = element;
		this.options = $.extend({}, defaults, options);

		this._defaults = defaults;
		this._name = pluginName;

		this.init();
	}

	Plugin.prototype = {
		init: function() {
			this.options.name = pluginName + '_' + Math.floor(Math.random() * 1e9);

			this._defineElements();
			this._defineGetters();
			this._defineSetters();
			this._handleWindowLoadAndResize();
			this._detectViewport();

			this.refresh({ firstLoad: true });

			if (this.options.scrollProperty === 'scroll') {
				this._handleScrollEvent();
			} else {
				this._startAnimationLoop();
			}
		},
		_defineElements: function() {
			if (this.element === document.body) this.element = window;
			this.$scrollElement = $(this.element);
			this.$element = (this.element === window ? $('body') : this.$scrollElement);
			this.$viewportElement = (this.options.viewportElement !== undefined ? $(this.options.viewportElement) : (this.$scrollElement[0] === window || this.options.scrollProperty === 'scroll' ? this.$scrollElement : this.$scrollElement.parent()) );
		},
		_defineGetters: function() {
			var self = this,
				scrollPropertyAdapter = scrollProperty[self.options.scrollProperty];

			this._getScrollLeft = function() {
				return scrollPropertyAdapter.getLeft(self.$scrollElement);
			};

			this._getScrollTop = function() {
				return scrollPropertyAdapter.getTop(self.$scrollElement);
			};
		},
		_defineSetters: function() {
			var self = this,
				scrollPropertyAdapter = scrollProperty[self.options.scrollProperty],
				positionPropertyAdapter = positionProperty[self.options.positionProperty],
				setScrollLeft = scrollPropertyAdapter.setLeft,
				setScrollTop = scrollPropertyAdapter.setTop;

			this._setScrollLeft = (typeof setScrollLeft === 'function' ? function(val) {
				setScrollLeft(self.$scrollElement, val);
			} : $.noop);

			this._setScrollTop = (typeof setScrollTop === 'function' ? function(val) {
				setScrollTop(self.$scrollElement, val);
			} : $.noop);

			this._setPosition = positionPropertyAdapter.setPosition ||
				function($elem, left, startingLeft, top, startingTop) {
					if (self.options.horizontalScrolling) {
						positionPropertyAdapter.setLeft($elem, left, startingLeft);
					}

					if (self.options.verticalScrolling) {
						positionPropertyAdapter.setTop($elem, top, startingTop);
					}
				};
		},
		_handleWindowLoadAndResize: function() {
			var self = this,
				$window = $(window);

			if (self.options.responsive) {
				$window.bind('load.' + this.name, function() {
					self.refresh();
				});
			}

			$window.bind('resize.' + this.name, function() {
				self._detectViewport();

				if (self.options.responsive) {
					self.refresh();
				}
			});
		},
		refresh: function(options) {
			var self = this,
				oldLeft = self._getScrollLeft(),
				oldTop = self._getScrollTop();

			if (!options || !options.firstLoad) {
				this._reset();
			}

			this._setScrollLeft(0);
			this._setScrollTop(0);

			this._setOffsets();
			this._findParticles();
			this._findBackgrounds();

			// Fix for WebKit background rendering bug
			if (options && options.firstLoad && /WebKit/.test(navigator.userAgent)) {
				$(window).load(function() {
					var oldLeft = self._getScrollLeft(),
						oldTop = self._getScrollTop();

					self._setScrollLeft(oldLeft + 1);
					self._setScrollTop(oldTop + 1);

					self._setScrollLeft(oldLeft);
					self._setScrollTop(oldTop);
				});
			}

			this._setScrollLeft(oldLeft);
			this._setScrollTop(oldTop);
		},
		_detectViewport: function() {
			var viewportOffsets = this.$viewportElement.offset(),
				hasOffsets = viewportOffsets !== null && viewportOffsets !== undefined;

			this.viewportWidth = this.$viewportElement.width();
			this.viewportHeight = this.$viewportElement.height();

			this.viewportOffsetTop = (hasOffsets ? viewportOffsets.top : 0);
			this.viewportOffsetLeft = (hasOffsets ? viewportOffsets.left : 0);
		},
		_findParticles: function() {
			var self = this,
				scrollLeft = this._getScrollLeft(),
				scrollTop = this._getScrollTop();

			if (this.particles !== undefined) {
				for (var i = this.particles.length - 1; i >= 0; i--) {
					this.particles[i].$element.data('stellar-elementIsActive', undefined);
				}
			}

			this.particles = [];

			if (!this.options.parallaxElements) return;

			this.$element.find('[data-stellar-ratio]').each(function(i) {
				var $this = $(this),
					horizontalOffset,
					verticalOffset,
					positionLeft,
					positionTop,
					marginLeft,
					marginTop,
					$offsetParent,
					offsetLeft,
					offsetTop,
					parentOffsetLeft = 0,
					parentOffsetTop = 0,
					tempParentOffsetLeft = 0,
					tempParentOffsetTop = 0;

				// Ensure this element isn't already part of another scrolling element
				if (!$this.data('stellar-elementIsActive')) {
					$this.data('stellar-elementIsActive', this);
				} else if ($this.data('stellar-elementIsActive') !== this) {
					return;
				}

				self.options.showElement($this);

				// Save/restore the original top and left CSS values in case we refresh the particles or destroy the instance
				if (!$this.data('stellar-startingLeft')) {
					$this.data('stellar-startingLeft', $this.css('left'));
					$this.data('stellar-startingTop', $this.css('top'));
				} else {
					$this.css('left', $this.data('stellar-startingLeft'));
					$this.css('top', $this.data('stellar-startingTop'));
				}

				positionLeft = $this.position().left;
				positionTop = $this.position().top;

				// Catch-all for margin top/left properties (these evaluate to 'auto' in IE7 and IE8)
				marginLeft = ($this.css('margin-left') === 'auto') ? 0 : parseInt($this.css('margin-left'), 10);
				marginTop = ($this.css('margin-top') === 'auto') ? 0 : parseInt($this.css('margin-top'), 10);

				offsetLeft = $this.offset().left - marginLeft;
				offsetTop = $this.offset().top - marginTop;

				// Calculate the offset parent
				$this.parents().each(function() {
					var $this = $(this);

					if ($this.data('stellar-offset-parent') === true) {
						parentOffsetLeft = tempParentOffsetLeft;
						parentOffsetTop = tempParentOffsetTop;
						$offsetParent = $this;

						return false;
					} else {
						tempParentOffsetLeft += $this.position().left;
						tempParentOffsetTop += $this.position().top;
					}
				});

				// Detect the offsets
				horizontalOffset = ($this.data('stellar-horizontal-offset') !== undefined ? $this.data('stellar-horizontal-offset') : ($offsetParent !== undefined && $offsetParent.data('stellar-horizontal-offset') !== undefined ? $offsetParent.data('stellar-horizontal-offset') : self.horizontalOffset));
				verticalOffset = ($this.data('stellar-vertical-offset') !== undefined ? $this.data('stellar-vertical-offset') : ($offsetParent !== undefined && $offsetParent.data('stellar-vertical-offset') !== undefined ? $offsetParent.data('stellar-vertical-offset') : self.verticalOffset));

				// Add our object to the particles collection
				self.particles.push({
					$element: $this,
					$offsetParent: $offsetParent,
					isFixed: $this.css('position') === 'fixed',
					horizontalOffset: horizontalOffset,
					verticalOffset: verticalOffset,
					startingPositionLeft: positionLeft,
					startingPositionTop: positionTop,
					startingOffsetLeft: offsetLeft,
					startingOffsetTop: offsetTop,
					parentOffsetLeft: parentOffsetLeft,
					parentOffsetTop: parentOffsetTop,
					stellarRatio: ($this.data('stellar-ratio') !== undefined ? $this.data('stellar-ratio') : 1),
					width: $this.outerWidth(true),
					height: $this.outerHeight(true),
					isHidden: false
				});
			});
		},
		_findBackgrounds: function() {
			var self = this,
				scrollLeft = this._getScrollLeft(),
				scrollTop = this._getScrollTop(),
				$backgroundElements;

			this.backgrounds = [];

			if (!this.options.parallaxBackgrounds) return;

			$backgroundElements = this.$element.find('[data-stellar-background-ratio]');

			if (this.$element.data('stellar-background-ratio')) {
                $backgroundElements = $backgroundElements.add(this.$element);
			}

			$backgroundElements.each(function() {
				var $this = $(this),
					backgroundPosition = getBackgroundPosition($this),
					horizontalOffset,
					verticalOffset,
					positionLeft,
					positionTop,
					marginLeft,
					marginTop,
					offsetLeft,
					offsetTop,
					$offsetParent,
					parentOffsetLeft = 0,
					parentOffsetTop = 0,
					tempParentOffsetLeft = 0,
					tempParentOffsetTop = 0;

				// Ensure this element isn't already part of another scrolling element
				if (!$this.data('stellar-backgroundIsActive')) {
					$this.data('stellar-backgroundIsActive', this);
				} else if ($this.data('stellar-backgroundIsActive') !== this) {
					return;
				}

				// Save/restore the original top and left CSS values in case we destroy the instance
				if (!$this.data('stellar-backgroundStartingLeft')) {
					$this.data('stellar-backgroundStartingLeft', backgroundPosition[0]);
					$this.data('stellar-backgroundStartingTop', backgroundPosition[1]);
				} else {
					setBackgroundPosition($this, $this.data('stellar-backgroundStartingLeft'), $this.data('stellar-backgroundStartingTop'));
				}

				// Catch-all for margin top/left properties (these evaluate to 'auto' in IE7 and IE8)
				marginLeft = ($this.css('margin-left') === 'auto') ? 0 : parseInt($this.css('margin-left'), 10);
				marginTop = ($this.css('margin-top') === 'auto') ? 0 : parseInt($this.css('margin-top'), 10);

				offsetLeft = $this.offset().left - marginLeft - scrollLeft;
				offsetTop = $this.offset().top - marginTop - scrollTop;
				
				// Calculate the offset parent
				$this.parents().each(function() {
					var $this = $(this);

					if ($this.data('stellar-offset-parent') === true) {
						parentOffsetLeft = tempParentOffsetLeft;
						parentOffsetTop = tempParentOffsetTop;
						$offsetParent = $this;

						return false;
					} else {
						tempParentOffsetLeft += $this.position().left;
						tempParentOffsetTop += $this.position().top;
					}
				});

			});
		},
		_reset: function() {
			var particle,
				startingPositionLeft,
				startingPositionTop,
				background,
				i;

			for (i = this.particles.length - 1; i >= 0; i--) {
				particle = this.particles[i];
				startingPositionLeft = particle.$element.data('stellar-startingLeft');
				startingPositionTop = particle.$element.data('stellar-startingTop');

				this._setPosition(particle.$element, startingPositionLeft, startingPositionLeft, startingPositionTop, startingPositionTop);

				this.options.showElement(particle.$element);

				particle.$element.data('stellar-startingLeft', null).data('stellar-elementIsActive', null).data('stellar-backgroundIsActive', null);
			}

			for (i = this.backgrounds.length - 1; i >= 0; i--) {
				background = this.backgrounds[i];

				background.$element.data('stellar-backgroundStartingLeft', null).data('stellar-backgroundStartingTop', null);

				setBackgroundPosition(background.$element, background.startingValueLeft, background.startingValueTop);
			}
		},
		destroy: function() {
			this._reset();

			this.$scrollElement.unbind('resize.' + this.name).unbind('scroll.' + this.name);
			this._animationLoop = $.noop;

			$(window).unbind('load.' + this.name).unbind('resize.' + this.name);
		},
		_setOffsets: function() {
			var self = this,
				$window = $(window);

			$window.unbind('resize.horizontal-' + this.name).unbind('resize.vertical-' + this.name);

			if (typeof this.options.horizontalOffset === 'function') {
				this.horizontalOffset = this.options.horizontalOffset();
				$window.bind('resize.horizontal-' + this.name, function() {
					self.horizontalOffset = self.options.horizontalOffset();
				});
			} else {
				this.horizontalOffset = this.options.horizontalOffset;
			}

			if (typeof this.options.verticalOffset === 'function') {
				this.verticalOffset = this.options.verticalOffset();
				$window.bind('resize.vertical-' + this.name, function() {
					self.verticalOffset = self.options.verticalOffset();
				});
			} else {
				this.verticalOffset = this.options.verticalOffset;
			}
		},
		_repositionElements: function() {
			var scrollLeft = this._getScrollLeft(),
				scrollTop = this._getScrollTop(),
				horizontalOffset,
				verticalOffset,
				particle,
				fixedRatioOffset,
				background,
				bgLeft,
				bgTop,
				isVisibleVertical = true,
				isVisibleHorizontal = true,
				newPositionLeft,
				newPositionTop,
				newOffsetLeft,
				newOffsetTop,
				i;

			// First check that the scroll position or container size has changed
			if (this.currentScrollLeft === scrollLeft && this.currentScrollTop === scrollTop && this.currentWidth === this.viewportWidth && this.currentHeight === this.viewportHeight) {
				return;
			} else {
				this.currentScrollLeft = scrollLeft;
				this.currentScrollTop = scrollTop;
				this.currentWidth = this.viewportWidth;
				this.currentHeight = this.viewportHeight;
			}

			// Reposition elements
			for (i = this.particles.length - 1; i >= 0; i--) {
				particle = this.particles[i];

				fixedRatioOffset = (particle.isFixed ? 1 : 0);

				// Calculate position, then calculate what the particle's new offset will be (for visibility check)
				if (this.options.horizontalScrolling) {
					newPositionLeft = (scrollLeft + particle.horizontalOffset + this.viewportOffsetLeft + particle.startingPositionLeft - particle.startingOffsetLeft + particle.parentOffsetLeft) * -(particle.stellarRatio + fixedRatioOffset - 1) + particle.startingPositionLeft;
					newOffsetLeft = newPositionLeft - particle.startingPositionLeft + particle.startingOffsetLeft;
				} else {
					newPositionLeft = particle.startingPositionLeft;
					newOffsetLeft = particle.startingOffsetLeft;
				}

				if (this.options.verticalScrolling) {
					newPositionTop = (scrollTop + particle.verticalOffset + this.viewportOffsetTop + particle.startingPositionTop - particle.startingOffsetTop + particle.parentOffsetTop) * -(particle.stellarRatio + fixedRatioOffset - 1) + particle.startingPositionTop;
					newOffsetTop = newPositionTop - particle.startingPositionTop + particle.startingOffsetTop;
				} else {
					newPositionTop = particle.startingPositionTop;
					newOffsetTop = particle.startingOffsetTop;
				}

				// Check visibility
				if (this.options.hideDistantElements) {
					isVisibleHorizontal = !this.options.horizontalScrolling || newOffsetLeft + particle.width > (particle.isFixed ? 0 : scrollLeft) && newOffsetLeft < (particle.isFixed ? 0 : scrollLeft) + this.viewportWidth + this.viewportOffsetLeft;
					isVisibleVertical = !this.options.verticalScrolling || newOffsetTop + particle.height > (particle.isFixed ? 0 : scrollTop) && newOffsetTop < (particle.isFixed ? 0 : scrollTop) + this.viewportHeight + this.viewportOffsetTop;
				}

				if (isVisibleHorizontal && isVisibleVertical) {
					if (particle.isHidden) {
						this.options.showElement(particle.$element);
						particle.isHidden = false;
					}

					this._setPosition(particle.$element, newPositionLeft, particle.startingPositionLeft, newPositionTop, particle.startingPositionTop);
				} else {
					if (!particle.isHidden) {
						this.options.hideElement(particle.$element);
						particle.isHidden = true;
					}
				}
			}

			// Reposition backgrounds
			for (i = this.backgrounds.length - 1; i >= 0; i--) {
				background = this.backgrounds[i];

				fixedRatioOffset = (background.isFixed ? 0 : 1);
				bgLeft = (this.options.horizontalScrolling ? (scrollLeft + background.horizontalOffset - this.viewportOffsetLeft - background.startingOffsetLeft + background.parentOffsetLeft - background.startingBackgroundPositionLeft) * (fixedRatioOffset - background.stellarRatio) + 'px' : background.startingValueLeft);
				bgTop = (this.options.verticalScrolling ? (scrollTop + background.verticalOffset - this.viewportOffsetTop - background.startingOffsetTop + background.parentOffsetTop - background.startingBackgroundPositionTop) * (fixedRatioOffset - background.stellarRatio) + 'px' : background.startingValueTop);

				setBackgroundPosition(background.$element, bgLeft, bgTop);
			}
		},
		_handleScrollEvent: function() {
			var self = this,
				ticking = false;

			var update = function() {
				self._repositionElements();
				ticking = false;
			};

			var requestTick = function() {
				if (!ticking) {
					requestAnimFrame(update);
					ticking = true;
				}
			};
			
			this.$scrollElement.bind('scroll.' + this.name, requestTick);
			requestTick();
		},
		_startAnimationLoop: function() {
			var self = this;

			this._animationLoop = function() {
				requestAnimFrame(self._animationLoop);
				self._repositionElements();
			};
			this._animationLoop();
		}
	};

	$.fn[pluginName] = function (options) {
		var args = arguments;
		if (options === undefined || typeof options === 'object') {
			return this.each(function () {
				if (!$.data(this, 'plugin_' + pluginName)) {
					$.data(this, 'plugin_' + pluginName, new Plugin(this, options));
				}
			});
		} else if (typeof options === 'string' && options[0] !== '_' && options !== 'init') {
			return this.each(function () {
				var instance = $.data(this, 'plugin_' + pluginName);
				if (instance instanceof Plugin && typeof instance[options] === 'function') {
					instance[options].apply(instance, Array.prototype.slice.call(args, 1));
				}
				if (options === 'destroy') {
					$.data(this, 'plugin_' + pluginName, null);
				}
			});
		}
	};

	$[pluginName] = function(options) {
		var $window = $(window);
		return $window.stellar.apply($window, Array.prototype.slice.call(arguments, 0));
	};

	// Expose the scroll and position property function hashes so they can be extended
	$[pluginName].scrollProperty = scrollProperty;
	$[pluginName].positionProperty = positionProperty;

	// Expose the plugin class so it can be modified
	window.Stellar = Plugin;
}(jQuery, this, document));


