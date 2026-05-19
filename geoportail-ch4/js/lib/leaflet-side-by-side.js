/*!
 * leaflet-side-by-side v2.2.0
 * Compare two Leaflet layers side by side
 * https://github.com/digidem/leaflet-side-by-side
 *
 * Version browser autonome (CSS injecté inline, sans require/module).
 */
(function () {
  if (typeof L === 'undefined') {
    console.error('[leaflet-side-by-side] Leaflet (L) introuvable.');
    return;
  }

  // ────────── CSS inline ──────────
  var CSS = [
    '.leaflet-sbs-range{position:absolute;top:50%;width:100%;z-index:999;-webkit-appearance:none;display:inline-block!important;vertical-align:middle;height:0;padding:0;margin:0;border:0;background:rgba(0,0,0,0.25);min-width:100px;cursor:pointer;pointer-events:none}',
    '.leaflet-sbs-divider{position:absolute;top:0;bottom:0;left:50%;margin-left:-2px;width:4px;background-color:#fff;pointer-events:none;z-index:999}',
    '.leaflet-sbs-range::-ms-fill-upper{background:transparent}',
    '.leaflet-sbs-range::-ms-fill-lower{background:rgba(255,255,255,0.25)}',
    '.leaflet-sbs-range::-moz-range-track{opacity:0}',
    '.leaflet-sbs-range::-ms-track{opacity:0}',
    '.leaflet-sbs-range::-ms-tooltip{display:none}',
    '.leaflet-sbs-range::-webkit-slider-thumb{-webkit-appearance:none;margin:0;padding:0;background:#fff;height:40px;width:40px;border-radius:20px;cursor:ew-resize;pointer-events:auto;border:1px solid #ddd;background-image:url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'40\' height=\'40\' viewBox=\'0 0 40 40\'><g fill=\'none\' stroke=\'%23666\' stroke-width=\'2\' stroke-linecap=\'round\'><path d=\'M15 14 L11 20 L15 26\'/><path d=\'M25 14 L29 20 L25 26\'/></g></svg>");background-position:50% 50%;background-repeat:no-repeat;background-size:40px 40px}',
    '.leaflet-sbs-range::-ms-thumb{margin:0;padding:0;background:#fff;height:40px;width:40px;border-radius:20px;cursor:ew-resize;pointer-events:auto;border:1px solid #ddd;background-image:url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'40\' height=\'40\' viewBox=\'0 0 40 40\'><g fill=\'none\' stroke=\'%23666\' stroke-width=\'2\' stroke-linecap=\'round\'><path d=\'M15 14 L11 20 L15 26\'/><path d=\'M25 14 L29 20 L25 26\'/></g></svg>");background-position:50% 50%;background-repeat:no-repeat;background-size:40px 40px}',
    '.leaflet-sbs-range::-moz-range-thumb{padding:0;right:0;background:#fff;height:40px;width:40px;border-radius:20px;cursor:ew-resize;pointer-events:auto;border:1px solid #ddd;background-image:url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'40\' height=\'40\' viewBox=\'0 0 40 40\'><g fill=\'none\' stroke=\'%23666\' stroke-width=\'2\' stroke-linecap=\'round\'><path d=\'M15 14 L11 20 L15 26\'/><path d=\'M25 14 L29 20 L25 26\'/></g></svg>");background-position:50% 50%;background-repeat:no-repeat;background-size:40px 40px}',
    '.leaflet-sbs-range:disabled::-moz-range-thumb,.leaflet-sbs-range:disabled::-ms-thumb,.leaflet-sbs-range:disabled::-webkit-slider-thumb,.leaflet-sbs-range:disabled{cursor:default}',
    '.leaflet-sbs-range:focus{outline:none!important}',
    '.leaflet-sbs-range::-moz-focus-outer{border:0}'
  ].join('\n');
  var style = document.createElement('style');
  style.textContent = CSS;
  document.head.appendChild(style);

  // ────────── Plugin code ──────────
  var mapWasDragEnabled;
  var mapWasTapEnabled;

  function on (el, types, fn, context) {
    types.split(' ').forEach(function (type) {
      L.DomEvent.on(el, type, fn, context);
    });
  }
  function off (el, types, fn, context) {
    types.split(' ').forEach(function (type) {
      L.DomEvent.off(el, type, fn, context);
    });
  }
  function getRangeEvent (rangeInput) {
    return 'oninput' in rangeInput ? 'input' : 'change';
  }
  function cancelMapDrag () {
    mapWasDragEnabled = this._map.dragging.enabled();
    mapWasTapEnabled = this._map.tap && this._map.tap.enabled();
    this._map.dragging.disable();
    this._map.tap && this._map.tap.disable();
  }
  function uncancelMapDrag (e) {
    this._refocusOnMap(e);
    if (mapWasDragEnabled) this._map.dragging.enable();
    if (mapWasTapEnabled)  this._map.tap.enable();
  }
  function asArray (arg) {
    return (arg === 'undefined') ? [] : Array.isArray(arg) ? arg : [arg];
  }
  function noop () {}

  L.Control.SideBySide = L.Control.extend({
    options: {
      thumbSize: 42,
      padding: 0
    },

    initialize: function (leftLayers, rightLayers, options) {
      this.setLeftLayers(leftLayers);
      this.setRightLayers(rightLayers);
      L.setOptions(this, options);
    },

    getPosition: function () {
      var rangeValue = this._range.value;
      var offset = (0.5 - rangeValue) * (2 * this.options.padding + this.options.thumbSize);
      return this._map.getSize().x * rangeValue + offset;
    },

    setPosition: noop,

    includes: L.Evented.prototype || L.Mixin.Events,

    addTo: function (map) {
      this.remove();
      this._map = map;

      var container = this._container = L.DomUtil.create('div', 'leaflet-sbs', map._controlContainer);

      this._divider = L.DomUtil.create('div', 'leaflet-sbs-divider', container);
      var range = this._range = L.DomUtil.create('input', 'leaflet-sbs-range', container);
      range.type = 'range';
      range.min = 0;
      range.max = 1;
      range.step = 'any';
      range.value = 0.5;
      range.style.paddingLeft = range.style.paddingRight = this.options.padding + 'px';
      this._addEvents();
      this._updateLayers();
      return this;
    },

    remove: function () {
      if (!this._map) return this;
      if (this._leftLayer)  this._leftLayer.getContainer().style.clip = '';
      if (this._rightLayer) this._rightLayer.getContainer().style.clip = '';
      this._removeEvents();
      L.DomUtil.remove(this._container);
      this._map = null;
      return this;
    },

    setLeftLayers: function (leftLayers) {
      this._leftLayers = asArray(leftLayers);
      this._updateLayers();
      return this;
    },

    setRightLayers: function (rightLayers) {
      this._rightLayers = asArray(rightLayers);
      this._updateLayers();
      return this;
    },

    _updateClip: function () {
      var map = this._map;
      var nw = map.containerPointToLayerPoint([0, 0]);
      var se = map.containerPointToLayerPoint(map.getSize());
      var clipX = nw.x + this.getPosition();
      var dividerX = this.getPosition();

      this._divider.style.left = dividerX + 'px';
      this.fire('dividermove', { x: dividerX });
      var clipLeft  = 'rect(' + [nw.y, clipX, se.y, nw.x].join('px,') + 'px)';
      var clipRight = 'rect(' + [nw.y, se.x, se.y, clipX].join('px,') + 'px)';
      if (this._leftLayer)  this._leftLayer.getContainer().style.clip  = clipLeft;
      if (this._rightLayer) this._rightLayer.getContainer().style.clip = clipRight;
    },

    _updateLayers: function () {
      if (!this._map) return this;
      var prevLeft  = this._leftLayer;
      var prevRight = this._rightLayer;
      this._leftLayer = this._rightLayer = null;
      this._leftLayers.forEach(function (layer) {
        if (this._map.hasLayer(layer)) this._leftLayer = layer;
      }, this);
      this._rightLayers.forEach(function (layer) {
        if (this._map.hasLayer(layer)) this._rightLayer = layer;
      }, this);
      if (prevLeft !== this._leftLayer) {
        prevLeft && this.fire('leftlayerremove', { layer: prevLeft });
        this._leftLayer && this.fire('leftlayeradd', { layer: this._leftLayer });
      }
      if (prevRight !== this._rightLayer) {
        prevRight && this.fire('rightlayerremove', { layer: prevRight });
        this._rightLayer && this.fire('rightlayeradd', { layer: this._rightLayer });
      }
      this._updateClip();
    },

    _addEvents: function () {
      var range = this._range;
      var map = this._map;
      if (!map || !range) return;
      map.on('move', this._updateClip, this);
      map.on('layeradd layerremove', this._updateLayers, this);
      L.DomEvent.on(range, getRangeEvent(range), this._updateClip, this);
      L.DomEvent.on(range, 'touchstart', cancelMapDrag, this);
      L.DomEvent.on(range, 'touchend',   uncancelMapDrag, this);
      L.DomEvent.on(range, 'mousedown',  cancelMapDrag, this);
      L.DomEvent.on(range, 'mouseup',    uncancelMapDrag, this);
    },

    _removeEvents: function () {
      var range = this._range;
      var map = this._map;
      if (range) {
        L.DomEvent.off(range, getRangeEvent(range), this._updateClip, this);
        L.DomEvent.off(range, 'touchstart', cancelMapDrag, this);
        L.DomEvent.off(range, 'touchend',   uncancelMapDrag, this);
        L.DomEvent.off(range, 'mousedown',  cancelMapDrag, this);
        L.DomEvent.off(range, 'mouseup',    uncancelMapDrag, this);
      }
      if (map) {
        map.off('layeradd layerremove', this._updateLayers, this);
        map.off('move', this._updateClip, this);
      }
    }
  });

  L.control.sideBySide = function (leftLayers, rightLayers, options) {
    return new L.Control.SideBySide(leftLayers, rightLayers, options);
  };
})();
