//	::export DragMixin, DropMixin
//	::style uiutils.dnd

let DragManager = (() => {
	class DragManager {
		constructor() {
			this.dragData = null;
			this.element = null;
			this.drops = [];

			cv.onceReady(this.attachEventListeners.bind(this));
		}

		addDrop(drop) {
			this.drops.push(this);
		}

		attachEventListeners() {
			document.body.addEventListener('mousemove', event => {
				if (!this.element) return;
				event.preventDefault();
				
				this.element.style.position = 'fixed';
				this.element.style.top = event.clientY + 'px';
				this.element.style.left = event.clientX + 'px';
			});

			document.body.addEventListener('mouseup', this.popDrag.bind(this));
		}

		peekDrag() {
			return this.dragData;
		}

		popDrag() {
			if (!this.element) return null;
			document.body.className = '';
			cv.iter(this.drops, drop => {
				drop.host.state.dnd.target = false;
			});
			
			document.body.removeChild(this.element);
			this.element = null;

			let data = this.dragData;
			this.dragData = null;
			return data;
		}

		newDrag(view, dataType, context) {
			this.popDrag();
			document.body.className = 'dnd-active';
			let dataPkg = view.getDragData(context);

			this.element = cv.render(
				<div class="dnd-dragging">
					{ view.__dragTemplate(dataPkg) }
				</div>
			)
			document.body.appendChild(this.element);
			this.element.style.position = 'fixed';
			this.element.style.top = context.event.clientY + 'px';
			this.element.style.left = context.event.clientX + 'px';
			this.element.style.pointerEvents = 'none';

			this.dragData = {
				type: dataType,
				content: dataPkg
			}
		}
	}

	return new DragManager();
})();

class DragMixin {
	constructor(options) {
		this.dataType = options.type;
		this.template = options.dragged;
	}

	attachToHost(host) {
		host.__drag__ = context => DragManager.newDrag(host, this.dataType, context);
		host.__dragTemplate = this.template;
		host.getDragData = host.getDragData || (() => host.data);

		host.__events__ = host.__events__ || []; // TODO: Shouldn't be nessesary.
		host.__events__.push(['.dnd-drag', 'mousedown', '__drag__']);
	}
}

class DropMixin {
	constructor(...acceptTypes) {
		this.acceptTypes = acceptTypes;
	}

	updateHostOptions(options) {
		options.state = options.state || {};
		options.state.dndTarget = false;
	}

	attachToHost(host) {
		host.__checkDrop__ = context => {
			let drag = DragManager.peekDrag();
			if (!drag) return;
			if (this.acceptTypes.indexOf(drag.type) >= 0) {
				host.state.dndTarget = true;
			}
		}
		host.__unfocusDrop__ = context => {
			host.state.dndTarget = false;
		}
		host.__drop__ = context => {
			let drag = DragManager.popDrag();
			if (!drag) return;

			host.acceptDrop(drag.content);

			context.event.stopPropagation();
		}

		host.__events__ = host.__events__ || [];
		host.__events__.push(
			['.dnd-drop', 'mouseenter', '__checkDrop__'],
			['.dnd-drop', 'mouseup', '__drop__'],
			['.dnd-drop', 'mouseleave', '__unfocusDrop__']
		)
	}
}