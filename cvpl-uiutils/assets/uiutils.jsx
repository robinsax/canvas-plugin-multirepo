//	::export ListView, ListControls, ListItemMixin, ModedForm, ContextMenu

log = cv.logger('uiutils');

@cv.view({
	state: {
		itemView: null,
		properList: false,
		controls: null,
		count: -1,
		offset: 0,
		after: null,
		empty: null,
		filter: x => x
	},
	macros: {
		item: item => <div class="item">{ JSON.stringify(item) }</div>,
		listContent: (data, state, macros) =>
			<span>
				<span class={ state.filter(data).length == 0 ? "" : " hidden" }>
					{ state.empty ? state.empty : 
						<p class="align-center subtext nothing-to-show">Nothing to show</p>
					}
				</span>
				{ cv.comp(state.filter(data), (item => 
					state.itemView ? new state.itemView(item) : macros.item(item)
				), state.offset, state.offset + state.count) }
			</span>
	},
	template: (data, state, macros) =>
		<div class="list">
			{ state.controls ? state.controls : <span/> }
			{ state.properList ? 
				<ul class="items">
					{ macros.listContent(data, state, macros) }
				</ul>
				:
				<div class="items">
					{ macros.listContent(data, state, macros) }
				</div>
			}
			<span/>
			{ state.after ? state.after : <span/> }
		</div>
})
class ListView {
	attachToParent(parent) { parent[this.reference] = this; }
	
	onceConstructed(options) {
		this.state.itemView = options.itemView || null;
		this.state.count = options.count || -1;
		this.state.properList = options.properList || false;
		this.state.controls = options.controls || null;
		this.state.after = options.after || null;
		this.state.empty = options.empty || null;
		this.reference = options.reference || 'list';

		this.data = options.data;
		this.itemStates = {};
	}

	update(stateUpdates) {
		this.state.update(stateUpdates);
	}

	get length() {
		return this.state.filter(this.data).length;
	}
}

@cv.view({
	state: {
		pageLength: -1,
		currentPage: 0,
		pageCount: 1,
		search: null,
		classes: ""
	},
	template: (state, macros) =>
		<div class={ "lc-controls " + state.classes }>
			{ macros.refresh ?
				<span class="lc-refresh">{ macros.refresh }</span> 
				: 
				<i/>
			}
			{ macros.search ?
				typeof macros.search == 'function' ? macros.search(state.search) : macros.search
				:
				<span/>
			}
			{ macros.paging ?
				macros.paging(state.currentPage, state.pageCount)
				:
				<span/>
			}
		</div>
})
class ListControls {
	onceConstructed(options) {
		this.state.pageLength = options.pageLength || -1;
		this.state.classes = options.classes || "";
		this.macros = {
			refresh: null,
			paging: null,
			search: null
		};
		this.macros.refresh = options.refresh || null;
		this.macros.paging = options.paging || null;
		this.macros.search = options.search || null;
		this.searchCheck = options.searchCheck || null;
	}

	attachToParent(parent) {
		parent.controls = this; 
		parent.onceFetched = this.updateState.bind(this);
	}

	@cv.event('.lc-refresh')
	refreshList() {
		this.parent.fetch();
	}

	updateState(update={}) {
		this.state.update(update);
		this.parent.update({
			count: this.state.pageLength,
			offset: this.state.pageLength*this.state.currentPage,
			filter: this.state.search === null ? x => x : (search =>
				items => cv.comp(items, item => this.searchCheck(item, search) ? item : undefined)
			)(this.state.search)
		});
		this.state.pageCount = Math.max(1, Math.ceil(this.parent.length / this.state.pageLength));
		if (this.state.pageCount < this.state.currentPage) {
			this.state.currentPage = this.state.pageCount;
			this.parent.update({
				offset: this.state.currentPage*this.state.pageLength
			});
		}
	}

	@cv.event('.next')
	next() {
		this.updateState({
			currentPage: this.state.currentPage + 1
		});
	}

	@cv.event('.prev')
	prev() {
		this.updateState({
			currentPage: this.state.currentPage - 1
		});
	}

	@cv.event('.search', 'change')
	@cv.event('.search', 'keyup')
	updateSearch(context) {
		this.updateState({
			search: context.element.value
		});
	}
}

class ListItemMixin {
	constructor(key='id') { this.key = key; }

	attachToHost(host) {
		host.data = this.hostArguments[0];

		host.isStateDefault = host.isStateDefault || (() => true);
		
		let innerBeforeDestroyed = host.beforeDestroyed;
		host.beforeDestroyed = (function() {
			if (this.isStateDefault()) return;
			this.parent.itemStates[this.data[this.key]] = this.state.bind(() => {}).observe();
			innerBeforeDestroyed();
		}).bind(host);

		let innerOnceCreated = host.onceCreated;
		host.onceCreated = (function() {
			let state = this.parent.itemStates[this.data[this.key]];
			if (state) {
				this.state = state.bind(this.render.bind(this)).observe();
			}
			
			this.render();
			innerOnceCreated();
		}).bind(host);

		host.hasChanged = () => true;
	}
}

@cv.view({
	state: {
		editing: false,
		title: e => !e ? "Create" : "Edit",
		fields: [[], []],
		buttonLabels: ["Save Changes", "Create"],
		classes: ""
	},
	template: state =>
		<div class={ "form " + state.classes }>
			<h2>{ state.title(state.editing) }</h2>
			<div class="fields">
				{ state.fields }
			</div>
			<div class="align-right">
				<button class="submit">{ state.buttonLabels[state.editing ? 0 : 1] }</button>
			</div>
		</div>
})
class ModedForm {
	attachToParent(parent) { parent[this.reference] = this; }
	
	onceConstructed(options) {
		if (options.model) {
			log.warning('model option is deprecated, use formModel');
			options.formModel = options.model;
		}

		if (options.modal) {
			this.modalness = new cv.ModalMixin();
			this.state.open = false;
			this.modalness.attachToHost(this);
			this.reference = options.reference || 'form';
			delete options.modal;
		}
		this.formModel = options.formModel;
		this.url = options.url;
		this.method = options.method;
		this.extrasGenerator = options.extras || (() => { return {}; });
		this.parentSuccessCallback = options.parentSuccessCallback || 'childSubmitSuccess';
		this.submitSuccessCallback = options.submitSuccess || null;
		delete options.url;
		delete options.method;
		delete options.model;
		
		this.state.update(options);
	}

	get isEditing() {
		return !!this.state.editing;
	}

	@cv.event('.submit')
	submitForm() {
		super.submitForm( 
			(typeof this.method == "function" ?
				this.method(this.state.editing)
				:
				this.method
			),
			this.url(this.state.editing),
			this.extrasGenerator(this.state.editing, this)
		);
	}

	submitSuccess(response) {
		if (this.submitSuccessCallback) {
			this.submitSuccessCallback(response);
		}
		if (this.parent[this.parentSuccessCallback]) {
			this.parent[this.parentSuccessCallback](this.state.editing, response);
		}
		if (this.modalness) {
			this.close();
		}
	}

	setup(toEdit=null) {
		this.state.editing = toEdit;
		if (toEdit) {
			this.fillForm(toEdit);
		}
		else {
			this.clearForm();
		}
	}

	open(toEdit=null) {
		this.setup(toEdit);

		if (this.modalness) {
			this.state.open = true;
		}
	}
}

@cv.view({
	state: {active: false},
	template: (data, state) =>
		<div class={ "context-menu" + (!state.active ? " hidden" : "") }>
			{ cv.comp(data, item =>
				<div class="context-item">{ item }</div>	
			)}
		</div>
})
class ContextMenu {
	onceConstructed(options) {
		this.reference = options.reference || 'contextMenu';
		this.closeCallbacks = [];
		this.callbacks = [];
		this.data = [];
		this.wasOpened = false;

		cv.iter(options.items, item => {
			this.data.push(item[0]);
			this.callbacks.push(item[1]);
		});
	}

	onceClosed(callback) {
		this.closeCallbacks.push(callback);
	}

	onceCreated() {
		resources.loadStyle('uiutils.context_menus');
		this.closeListener = event => {
			if (this.wasOpened) {
				this.wasOpened = false;
				return;
			}
			if (event.hitContextMenu) return
			this.close();
		}
		document.body.addEventListener('click', this.closeListener);

		this.parent[this.reference] = this;
	}

	beforeDestroyed() {
		document.body.removeEventListener('click', this.closeListener);
	}

	@cv.event('.context-menu')
	keepOpen(context) {
		context.event.hitContextMenu = true;
	}

	@cv.event('.context-item')
	doItem(context) {
		this.callbacks[context.index](this);
		context.event.stopPropagation();
	}

	open() {
		this.state.active = true;
	}

	close() {
		this.state.active = false;
		cv.iter(this.closeCallbacks, callback => callback());
	}
}