

def get_user_progress(course, chapters):
    """
    Get user progress after mapping course details with user progress
    """
    user_course_progress = []
    if course and chapters:
        course_chapters = course.chapters
        for course_chapter in course_chapters:
            chapter = chapters.get(course_chapter.id)
            if chapter:
                user_course_progress.append(
                    {
                        'name': course_chapter.name,
                        'progress': (chapter['completion']['percent'] * 100)
                    }
                )
    return user_course_progress

