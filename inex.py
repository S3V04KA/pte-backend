import os
import glob

for file in glob.glob('./backend/docs/**/*.html', recursive=True):
    file = file.replace('\\', '/')
    print(file)
    with open(f'{file}', 'r', encoding='utf-8') as f:
      html = f.read()
    html = html.replace('<body style="margin: 0; padding: 10">', """<body style="margin: 0; padding: 10">
<<<<<<< HEAD
                         <div id="content" style="width: 100%">""")
=======
                        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
                        <script src="https://cdn.jsdelivr.net/g/jquery@3.1.0,mark.js@8.6.0(jquery.mark.min.js)" charset="UTF-8"></script>
                        <script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/8.11.1/mark.min.js" charset="UTF-8"></script>
                        <script>
                            var $input = $("input[type='search']"),
                                // clear button
                                $clearBtn = $("button[data-search='clear']"),
                                // prev button
                                $prevBtn = $("button[data-search='prev']"),
                                // next button
                                $nextBtn = $("button[data-search='next']"),
                                // the context where to search
                                $content = $("#content"),
                                // jQuery object to save <mark> elements
                                $results,
                                // the class that will be appended to the current
                                // focused element
                                currentClass = "current",
                                // top offset for the jump (the search bar)
                                offsetTop = 50,
                                // the current index of the focused element
                                currentIndex = 0;

                            function searchKeyword(keyword) {
                                var searchVal = keyword;
                                $content.unmark({
                                    iframes: true,
                                    done: function () {
                                        $content.mark(searchVal, {
                                            iframes: true,
                                            separateWordSearch: true,
                                            done: function () {
                                                $results = $content.find("mark");
                                                currentIndex = 0;
                                                jumpTo();
                                            }
                                        });
                                    }
                                });
                            }

                            function jumpTo() {
                                if ($results.length) {
                                    var position,
                                        $current = $results.eq(currentIndex);
                                    $results.removeClass(currentClass);
                                    if ($current.length) {
                                        $current.addClass(currentClass);
                                        position = $current.offset().top - offsetTop;
                                        window.scrollTo(0, position);
                                    }
                                }
                            }

                            function focusNext() {
                                if ($results.length) {
                                    console.log("length =", $results.length)
                                    currentIndex += 1;
                                    if (currentIndex < 0) {
                                        currentIndex = $results.length - 1;
                                    }
                                    if (currentIndex > $results.length - 1) {
                                        currentIndex = 0;
                                    }
                                    jumpTo();
                                }
                            }

                            function focusPrevious() {
                                if ($results.length) {
                                    console.log("length =", $results.length)
                                    currentIndex -= 1;
                                    if (currentIndex < 0) {
                                        currentIndex = $results.length - 1;
                                    }
                                    if (currentIndex > $results.length - 1) {
                                        currentIndex = 0;
                                    }
                                    jumpTo();
                                }
                            }

                            function unmark() {
                                var instance = new Mark('#content');
                                instance.unmark()
                            }
                        </script>
                        """)
>>>>>>> 4bd2bcc39dee7017a97c1ec458312d356b9b1869
    with open(f'{file}', 'w', encoding='utf-8') as f:
      f.write(html)