from __future__ import print_function
from distutils.core import setup
from distutils.command.install import install as _install
from distutils import log
from stat import ST_ATIME, ST_MTIME, S_IMODE, ST_MODE
import os, glob, sys
from chronoslnxlib import APPNAME,APPVERSION,AUTHOR,DESCRIPTION,YEAR,PAGE,EMAIL

# http://mammique.net/distutils_setup/
if sys.version_info < (3,0,0):
	print("Python 3.x is required!",file=sys.stderr)
	exit(1)

def globby_themes():
	file_pairs=[]
	for d in glob.glob(os.path.join('themes', '*')):
		put_here = os.path.join('share', 'chronoslnx', d)
		for f in glob.glob(os.path.join(d,'*')):
			if os.path.isdir(f):
				file_pairs.append((os.path.join(put_here, os.path.basename(f)), 
				glob.glob(os.path.join(f,'*'))))
			else:
				file_pairs.append((put_here, [os.path.join(d,'ui.css')]))

	return file_pairs

class install(_install):
	description = """Install and set constants"""
	user_options = _install.user_options

	def initialize_options(self):
		self.root = None
		self.install_data = None
		_install.initialize_options(self)

	def finalize_options(self):
		_install.finalize_options(self)

	def run (self):
		_install.run(self)

		# Rewrite with constants if needed
		for f in self.get_outputs():
			# If is package __init__.py file holding some constants
			if os.path.basename(f) == '__init__.py':
				script = open(f, encoding='utf-8')
				content = script.read()
				script.close()
				const_begin = content.find('### CONSTANTS BEGIN ###')
				const_end   = content.find('### CONSTANTS END ###')

				# If needs constants
				if (const_begin != -1) and (const_end != -1):
					log.info("Setting constants of %s" % f)

					at = os.stat(f) # Store attributes

					if self.install_data:
						replace_me = os.path.join(self.install_data,'share/chronoslnx')
					elif self.prefix:
						replace_me = os.path.join(self.prefix,'share/chronoslnx')

					if self.root == None:
						consts = [['DATA_DIR', replace_me.replace(os.sep,'/')]]
					elif self.root[-1] == '/':
						consts = [['DATA_DIR', replace_me.replace(self.root[:-2],'')]]
					else:
						consts = [['DATA_DIR', replace_me.replace(self.root,'')]]
					script = open(f, 'w', encoding='utf-8')
					script.write(content[:const_begin] + \
								 "### CONSTANTS BEGIN ###")

					for const in consts:
						script.write("\n{} = '{}'".format(const[0], const[1]))
					script.write("\n" + content[const_end:])
					script.close()

					# Restore attributes
					os.utime(f, (at[ST_ATIME], at[ST_MTIME]))
					os.chmod(f, S_IMODE(at[ST_MODE]))

data_files = [('share/applications',['ChronosLNX.desktop']),
			  ('share/pixmaps', ['themes/DarkGlyphs/misc/chronoslnx.png']),
			  ('share/chronoslnx', ['schedule.csv'])
			  ]
data_files.extend(globby_themes())
#print(data_files)

setup(
	name = APPNAME,
	version = APPVERSION,
	author = AUTHOR,
	author_email = EMAIL,
	description = DESCRIPTION,
	url = PAGE,
	packages = ['chronoslnxlib'],
	cmdclass={'install': install},
	data_files = data_files,
	scripts=['chronoslnx.py']
)

