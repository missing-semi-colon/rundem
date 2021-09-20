pkgname=rundem
pkgver=1.2
pkgrel=1
pkgdesc="curses-like interface to run commands"
arch=("any")
depends=("python")
makedepends=("python-setuptools")
md5sums=()

build() {
	cd ..
	python setup.py build
}

package() {
	site_packages_dir=$(python -c "import site; print(site.getsitepackages()[0])")

	cd ..
	python setup.py install --root="$pkgdir" --optimize=1 --skip-build
	
	mkdir -p "$pkgdir/etc/rundem"
	cp rundem/example "$pkgdir/etc/rundem/"
	cp rundem/example.sh "$pkgdir/etc/rundem/"
	chmod +x "$pkgdir/etc/rundem/example.sh"
	
	mkdir "$pkgdir/usr/bin/"
	echo "#!/usr/bin/sh" > "$pkgdir/usr/bin/rundem"
	echo "python ${site_packages_dir}/rundem/rundem.py" >> "$pkgdir/usr/bin/rundem"
	chmod +x "$pkgdir/usr/bin/rundem"
}
