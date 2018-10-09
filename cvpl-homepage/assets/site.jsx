//	::import uiutils

@cv.page('*', 'header')
@cv.view({
	data: [
		['/', 'Home'],
		['/start', 'Get Started'],
		['/docs', 'Docs'],
		['/plugins', 'Plugins']
	],
	state: {alt: 0, freeze: false},
	template: (data, state) =>
		<div class={ "content" + (state.freeze ? " freeze" : "") + (state.alt > 0 ? " alt-" + state.alt : "") }>
			<i class="fa fa-bars"/>
			<span class="left">
				{ cv.comp(data, link =>
					link[0] == cv.route ? undefined : <a class="clear vis" href={ link[0] }>{ link[1] }</a>
				) }
				{ window.user ? 
					<div class="inline-block relative">
						<span class="usership active">
							<a class="clear vis"><i class="fa fa-user vis"/> { window.user.username }</a>
							{ new uiutils.ContextMenu({
								reference: 'usershipMenu',
								items: [
									['My Dashboard', () => window.location = '/dashboard'],
									['My Account', () => window.location = '/account'],
									['Log Out', () => window.location = '/logout']
								]
							}) }
						</span>
					</div>
					:
					<span class="usership">
						<a class="clear vis" href="/login">Log in <i class="fa fa-sign-in vis"/></a>
					</span>
				}
			</span>
			<span class="right">
				<a class="clear" href="https://github.com/robinsax/canvas">
					<i class="fa fa-github"/>
				</a>
				<div class="badges">
					<img src="https://travis-ci.org/robinsax/canvas.svg?branch=master"/>
					<img src='https://coveralls.io/repos/github/robinsax/canvas/badge.svg?branch=master'/>
				</div>
			</span>
		</div>
})
class HeaderView {
	onceCreated() {
		if (cv.route == '/') {
			let callback = () => {
				let alt = 0, moreEl = document.querySelector('.more');
				if (!moreEl) return;

				if (moreEl.getBoundingClientRect().top <= 40) {
					alt = 2;
				}
				this.state.alt = alt;
			};

			window.addEventListener('mousewheel', callback);
			window.addEventListener('scroll', callback);
		}
	}

	@cv.event('.usership.active')
	openContext(context) {
		this.usershipMenu.open();
		context.event.stopPropagation();

		this.state.freeze = true;
		this.usershipMenu.onceClosed(() => this.state.freeze = false);
	}
}
