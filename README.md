# AIContentVerifier

### Program Structure
<img width="2816" height="1536" alt="Image" src="https://github.com/user-attachments/assets/4b13a569-997c-4f42-b983-256f215f8ee0" />


1. If client upload the sns post with images, server store the post info to mysql and image data to s3.  
2. Asynchronously detect AI-generated images using an external consumer and trigger tagging events.  
3. Another consumer stores images to preprocessed s3 after preprocessing.  
