# OpenFlexure Microscope Documentation
The documentation is best viewed [on openflexure.org][built_docs].  If you have problems or want to suggest improvements, please [raise an issue] or even better edit the markdown file in this folder and send us a pull request.

The assembly instructions are contained in this folder, in MarkDown format.  They use [Git-Building] to automatically generate the bill of materials, which means the markdown files will make sense if you view them directly, but you're better off using the [processed versions][built_docs] on openflexure.org.

If you would like to improve the documentation, the easiest way is to use the "edit" or "web IDE" features on GitLab, or you can fork the repository and work on it locally.  Bear in mind that this repository uses [Git LFS] and that, by default, it won't download the images for the documentation (before switching to LFS, it was a 1.5Gb download to clone the repository, which causes real problems for some of the team).  If you want to include the images in your repository, you can override the ``lfs.fetchexclude`` setting so that it will download them.  You should also make sure you have [Git LFS] installed.

```bash
git lfs install
git config --local lfs.fetchexclude "/docs/original_images,/design_files"
git lfs fetch
git lfs checkout
```

The block of code above will not download everything, as there is limited value in having the high-resolution original images unless you really need them.  Of course, you can modify the line that changes your git config to include that directory if you wish - but it is over 500Mb at the last count.

[built_docs]: https://www.openflexure.org/projects/microscope/docs/
[Git LFS]: https://git-lfs.github.com/
[Git-Building]: https://gitlab.com/bath_open_instrumentation_group/git-building
[raise an issue]: https://gitlab.com/openflexure/openflexure-microscope/issues/new