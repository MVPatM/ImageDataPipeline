from ..Config.db_config import get_db_session
from ..Model.Models import Post, Tag, PostTag
from sqlalchemy import select, update

class PostDAO:
    def get_post_by_image_url(self, image_url: str) -> Post:
        with get_db_session() as session:
            stmt = select(Post).where(Post.imageUrl == image_url)
            result = session.execute(stmt).scalar_one_or_none()
            if result:
                return result
            return None

    def update_post_status(self, post_id: int, status: str):
        with get_db_session() as session:
            stmt = update(Post).where(Post.id == post_id).values(status=status)
            session.execute(stmt)
            session.commit()
            print(f"Post {post_id} status updated to {status}")

    def add_tag_to_post(self, post_id: int, tag_name: str):
        with get_db_session() as session:
            try:
                # Find or Create Tag
                stmt = select(Tag).where(Tag.name == tag_name)
                tag = session.execute(stmt).scalar_one_or_none()
                
                if not tag:
                    tag = Tag(name=tag_name)
                    session.add(tag)
                    session.flush() 
                
                # Check if PostTag exists
                stmt = select(PostTag).where(PostTag.post_id == post_id, PostTag.tag_id == tag.id)
                post_tag = session.execute(stmt).scalar_one_or_none()
                
                if not post_tag:
                    post_tag = PostTag(post_id=post_id, tag_id=tag.id)
                    session.add(post_tag)
                    session.commit()
                    print(f"Added tag '{tag_name}' to Post {post_id}")
                else:
                    print(f"Tag '{tag_name}' already exists on Post {post_id}")
            except Exception as e:
                session.rollback()
                print(f"Error adding tag: {e}")
                raise
