//	::import !lib/d3.min
//	::load_palette default

const fullRegion = 1000, pointDelLimit = 100, delTime = 5000;
let nextID = 0;

class Node {
	constructor(origin, points, g) {
		this.g = g;
		this.className = 'g-' + (++nextID);
		this.origin = origin;
		this.points = points;

		let circles = this.g.selectAll('circle.' + this.className)
			.data(this.points).enter()
			.append('circle'),
		lines = this.g.selectAll('line.' + this.className)
			.data(d3.range(this.points.length - 1)).enter()
			.append('line');
		this.applyAttrs(circles, lines);
	}

	toCartesian(polar) {
		return {
			x: polar.r*Math.cos(polar.phi),
			y: polar.r*Math.sin(polar.phi)
		};
	}

	applyAttrs(circles, lines) {
		circles.attrs({
			class: this.className,
			r: '10px',
			fill: palette.theme1,
			cy: d => this.toCartesian(d).y + this.origin.y + 'px',
			cx: d => this.toCartesian(d).x + this.origin.x + 'px'
		});
		lines.attrs({
			class: this.className,
			stroke: palette.theme1,
			'stroke-width': '3px',
			y1: i => this.toCartesian(this.points[i]).y + this.origin.y + 'px',
			x1: i => this.toCartesian(this.points[i]).x + this.origin.x + 'px',
			y2: i => this.toCartesian(this.points[i + 1]).y + this.origin.y + 'px',
			x2: i => this.toCartesian(this.points[i + 1]).x + this.origin.x + 'px'
		})
	}

	update() {
		cv.iter(this.points, pt => {
			pt.phi += (Math.random() - 0.5) % Math.PI;
			pt.r += (Math.random() - 0.5)*pointDelLimit;
			pt.r = Math.min(pt.r, pointDelLimit);
		});
		
		let circles = this.g.selectAll('circle.' + this.className)
				.transition().ease(d3.easeLinear).duration(delTime),
			lines = this.g.selectAll('line.' + this.className)
				.transition().ease(d3.easeLinear).duration(delTime);
		this.applyAttrs(circles, lines);
	}
}

@cv.page('*')
@cv.view({
	template: () => <div class="decor-container"/>
})
class HomeDecorView {
	onceCreated() {
		this.g = d3.select(this.element).append('svg')
			//.attr('viewBox', '0 0 ' + fullRegion + ' ' + fullRegion)
			.append('g');

		this.nodes = cv.comp(d3.range(6 + (Math.floor(Math.random() * 6))), () => this.generateNode());

		setInterval(this.updateNodes.bind(this), delTime);
		this.updateNodes();
	}

	updateNodes() {
		cv.iter(this.nodes, node => node.update());
	}

	generatePolarPoint() {
		return {
			phi: Math.random()*Math.PI, 
			r: Math.random()*pointDelLimit
		};
	}

	generateCartesianPoint() {
		return {
			y: Math.random()*fullRegion, 
			x: Math.random()*fullRegion
		};
	}

	generateNode() {
		let origin = this.generateCartesianPoint(),
			pointDomain = d3.range(3 + Math.floor(Math.random()*3)),
			points = cv.comp(pointDomain, k => this.generatePolarPoint());
		
		return new Node(origin, points, this.g);
	}
}
