document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const progressBar = document.getElementById('progressBar');
    const translateBtn = document.getElementById('translateBtn');
    const loading = document.getElementById('loading');

    let currentSlide = 0;
    let currentLanguage = 'en'; // 'en' for English, 'zh' for Chinese

    // Touch/swipe variables
    let touchStartX = 0;
    let touchEndX = 0;
    let isSwiping = false;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove('active');
            if (i === index) {
                slide.classList.add('active');
            }
        });
        updateProgressBar();
        updateNavButtons();
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(currentSlide);
    }
    
    function updateProgressBar() {
        const percentage = ((currentSlide + 1) / slides.length) * 100;
        progressBar.style.width = `${percentage}%`;
    }

    function updateNavButtons() {
        // Hide prev on first slide, next on last slide
        prevBtn.style.display = currentSlide === 0 ? 'none' : 'flex';
        nextBtn.style.display = currentSlide === slides.length - 1 ? 'none' : 'flex';
    }

    function translateContent() {
        // Toggle language
        currentLanguage = currentLanguage === 'en' ? 'zh' : 'en';
        
        // Update button text
        translateBtn.textContent = currentLanguage === 'en' ? '中文' : 'English';
        
        // Find all elements with translation data attributes
        const translatableElements = document.querySelectorAll('[data-en][data-zh]');
        
        translatableElements.forEach(element => {
            const englishText = element.getAttribute('data-en');
            const chineseText = element.getAttribute('data-zh');
            
            if (currentLanguage === 'zh') {
                // Preserve SVG icons when translating
                const svgIcon = element.querySelector('.section-icon');
                element.textContent = chineseText;
                if (svgIcon) {
                    element.insertBefore(svgIcon, element.firstChild);
                }
            } else {
                // Preserve SVG icons when translating
                const svgIcon = element.querySelector('.section-icon');
                element.textContent = englishText;
                if (svgIcon) {
                    element.insertBefore(svgIcon, element.firstChild);
                }
            }
        });
        
        // Handle special cases for elements with mixed content (like strong tags inside)
        const mixedElements = document.querySelectorAll('li, p');
        mixedElements.forEach(element => {
            if (element.hasAttribute('data-en') && element.hasAttribute('data-zh')) {
                // Skip elements that were already handled above
                return;
            }
            
            // Handle elements that contain other translatable elements
            const childElements = element.querySelectorAll('[data-en][data-zh]');
            if (childElements.length > 0) {
                // Reconstruct the content based on current language
                let newContent = '';
                const englishContent = element.getAttribute('data-en') || '';
                const chineseContent = element.getAttribute('data-zh') || '';
                
                if (currentLanguage === 'zh' && chineseContent) {
                    newContent = chineseContent;
                } else if (englishContent) {
                    newContent = englishContent;
                }
                
                if (newContent) {
                    element.textContent = newContent;
                }
            }
        });

        // Handle code blocks translation
        translateCodeBlocks();
    }

    function translateCodeBlocks() {
        const codeBlocks = document.querySelectorAll('.code-block pre code');
        
        codeBlocks.forEach(codeBlock => {
            const codeText = codeBlock.textContent;
            
            // Define code translations
            const codeTranslations = {
                // Comments and strings
                'Vague Prompt': '模糊提示',
                'Good Prompt with Persona': '带角色的好提示',
                'Explain how a CPU works.': '解释CPU是如何工作的。',
                'You are a computer science professor teaching an introductory course.': '你是一位教授入门课程的计算机科学教授。',
                'Explain how a CPU works to a first-year student.': '向一年级学生解释CPU是如何工作的。',
                'Use an analogy to make it easier to understand.': '使用类比让它更容易理解。',
                'Act as an expert web developer.': '扮演一位专业的网页开发者。',
                'Create a single HTML file for a personal portfolio website for a developer named Alex Doe.': '为名为Alex Doe的开发者创建一个个人作品集网站的单一HTML文件。',
                'The website should have:': '网站应该包含：',
                'A navigation bar with links to "About", "Projects", and "Contact".': '一个包含"关于"、"项目"和"联系"链接的导航栏。',
                'An "About" section with a placeholder for a photo and a short bio.': '一个"关于"部分，包含照片占位符和简短的个人介绍。',
                'A "Projects" section that lists 3 projects with short descriptions.': '一个"项目"部分，列出3个项目并附简短描述。',
                'A "Contact" section with a simple contact form (Name, Email, Message).': '一个"联系"部分，包含简单的联系表单（姓名、邮箱、消息）。',
                'Use modern and clean HTML5 and CSS. All CSS should be in a `<style>` tag in the head of the document.': '使用现代简洁的HTML5和CSS。所有CSS都应该在文档头部的`<style>`标签中。',
                'Act as a Python game developer.': '扮演一位Python游戏开发者。',
                'Write the code for a simple text-based adventure game.': '编写一个简单的文字冒险游戏代码。',
                'The game should have:': '游戏应该包含：',
                'A player who can move between rooms.': '一个可以在房间之间移动的玩家。',
                'At least three rooms: "Cave Entrance", "Dark Tunnel", "Treasure Room".': '至少三个房间："洞穴入口"、"黑暗隧道"、"宝藏房间"。',
                'The player should be able to type commands like "go north", "go south".': '玩家应该能够输入"向北走"、"向南走"等命令。',
                'The goal is to find the treasure in the "Treasure Room".': '目标是在"宝藏房间"中找到宝藏。',
                'The code should be a single Python script.': '代码应该是一个单一的Python脚本。',
                'Load the pre-trained face detector': '加载预训练的人脸检测器',
                'Draw a rectangle around the faces': '在人脸周围绘制矩形',
                'Simple Prompt': '简单提示',
                'Detailed Prompt': '详细提示',
                'Result: A generic, likely simple drawing of an astronaut.': '结果：一个通用的、可能简单的宇航员图画。',
                'Result: A rich, cinematic, and specific image.': '结果：一个丰富、电影般且具体的图像。',
                'Example:': '示例：',
                'Self-driving cars detecting obstacles.': '自动驾驶汽车检测障碍物。',
                'Manufacturing for quality control.': '制造业质量控制。',
                'Augmented Reality filters on social media.': '社交媒体上的增强现实滤镜。',
                'Here is a Python script using OpenCV to detect faces in a webcam feed.': '这是一个使用OpenCV在摄像头画面中检测人脸的Python脚本。',
                'Bias:': '偏见：',
                'Privacy:': '隐私：',
                'Misinformation:': '虚假信息：',
                'Accountability:': '问责制：',
                'AI models can learn and amplify biases present in their training data.': 'AI模型可以学习并放大训练数据中存在的偏见。',
                'Systems that process personal data must be designed to be secure and protect privacy.': '处理个人数据的系统必须设计为安全且保护隐私。',
                'Generative models can be used to create convincing but false information.': '生成模型可用于创建令人信服但虚假的信息。',
                'Who is responsible when an AI system makes a mistake?': '当AI系统出错时，谁负责？',
                'Planning and executing a software project.': '规划和执行软件项目。',
                'Performing complex data analysis and generating a report.': '执行复杂的数据分析并生成报告。',
                'Automating research on a specific topic.': '自动化特定主题的研究。',
                'Goal:': '目标：',
                'Think:': '思考：',
                'Act:': '行动：',
                'Observe:': '观察：',
                'Repeat:': '重复：',
                'Receive a high-level objective from the user.': '从用户接收高级目标。',
                'Break down the goal into smaller, actionable steps.': '将目标分解为更小的、可操作的步骤。',
                'Execute a step (e.g., run code, search the web, write to a file).': '执行一个步骤（例如，运行代码、搜索网络、写入文件）。',
                'Analyze the result of the action.': '分析行动的结果。',
                'Adjust the plan based on the observation and continue until the goal is met.': '根据观察调整计划并继续直到目标达成。',
                'Thank You & Q&A': '谢谢 & 问答'
            };

            // Translate the code content
            let translatedCode = codeText;
            
            if (currentLanguage === 'zh') {
                // Replace English text with Chinese
                Object.keys(codeTranslations).forEach(english => {
                    const chinese = codeTranslations[english];
                    const regex = new RegExp(english.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
                    translatedCode = translatedCode.replace(regex, chinese);
                });
            } else {
                // Replace Chinese text with English
                Object.keys(codeTranslations).forEach(english => {
                    const chinese = codeTranslations[english];
                    const regex = new RegExp(chinese.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
                    translatedCode = translatedCode.replace(regex, english);
                });
            }
            
            codeBlock.textContent = translatedCode;
        });
    }

    // Touch/Swipe functionality for mobile
    function handleTouchStart(e) {
        touchStartX = e.changedTouches[0].screenX;
        isSwiping = true;
    }

    function handleTouchMove(e) {
        if (!isSwiping) return;
        
        touchEndX = e.changedTouches[0].screenX;
        const diffX = touchStartX - touchEndX;
        
        // Prevent default scrolling if swiping horizontally
        if (Math.abs(diffX) > 10) {
            e.preventDefault();
        }
    }

    function handleTouchEnd(e) {
        if (!isSwiping) return;
        
        touchEndX = e.changedTouches[0].screenX;
        const diffX = touchStartX - touchEndX;
        const minSwipeDistance = 50;
        
        if (Math.abs(diffX) > minSwipeDistance) {
            if (diffX > 0) {
                // Swiped left - next slide
                nextSlide();
            } else {
                // Swiped right - previous slide
                prevSlide();
            }
        }
        
        isSwiping = false;
    }

    // Keyboard navigation
    function handleKeyPress(e) {
        switch(e.key) {
            case 'ArrowRight':
            case ' ':
                e.preventDefault();
                nextSlide();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                prevSlide();
                break;
            case 't':
            case 'T':
                e.preventDefault();
                translateContent();
                break;
        }
    }

    // Add event listeners
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);
    translateBtn.addEventListener('click', translateContent);
    
    // Touch events for mobile
    document.addEventListener('touchstart', handleTouchStart, { passive: false });
    document.addEventListener('touchmove', handleTouchMove, { passive: false });
    document.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    // Keyboard events
    document.addEventListener('keydown', handleKeyPress);
    
    // Prevent context menu on long press for mobile
    document.addEventListener('contextmenu', e => e.preventDefault());

    // Initialize
    showSlide(currentSlide);
    
    // Hide loading indicator after content is ready
    setTimeout(() => {
        loading.classList.add('hidden');
        setTimeout(() => loading.remove(), 500);
    }, 1000);
    
    // Add swipe indicator for mobile
    if ('ontouchstart' in window) {
        const swipeIndicator = document.createElement('div');
        swipeIndicator.className = 'swipe-indicator';
        swipeIndicator.textContent = '← 滑动切换 →';
        swipeIndicator.setAttribute('data-en', '← Swipe to navigate →');
        swipeIndicator.setAttribute('data-zh', '← 滑动切换 →');
        document.body.appendChild(swipeIndicator);
        
        // Hide indicator after 3 seconds
        setTimeout(() => {
            swipeIndicator.style.opacity = '0';
            setTimeout(() => swipeIndicator.remove(), 1000);
        }, 3000);
    }
    
    // Preload images for better performance
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        if (img.src) {
            const preloadImg = new Image();
            preloadImg.src = img.src;
        }
    });
    
    // Add haptic feedback for mobile (if supported)
    if ('vibrate' in navigator) {
        const hapticFeedback = () => {
            navigator.vibrate(50);
        };
        
        nextBtn.addEventListener('click', hapticFeedback);
        prevBtn.addEventListener('click', hapticFeedback);
        translateBtn.addEventListener('click', hapticFeedback);
    }

    // Image Prompt Builder Logic
    const styleSelect = document.getElementById('styleSelect');
    const subjectSelect = document.getElementById('subjectSelect');
    const detailsSelect = document.getElementById('detailsSelect');
    const settingSelect = document.getElementById('settingSelect');
    const generatedPromptOutput = document.getElementById('generatedPrompt');

    function updateGeneratedPrompt() {
        const style = styleSelect.value;
        const subject = subjectSelect.value;
        const details = detailsSelect.value;
        const setting = settingSelect.value;

        let prompt = '';

        if (style) {
            prompt += `A ${style}`; 
        }

        if (subject) {
            prompt += ` of ${subject}`;
        }

        if (details) {
            prompt += ` ${details}`;
        }

        if (setting) {
            prompt += ` ${setting}`;
        }

        if (!style && !subject && !details && !setting) {
            generatedPromptOutput.textContent = '"A [Style] of [Subject] with [Details] in a [Setting]"'
        } else {
            generatedPromptOutput.textContent = `"${prompt.trim()}."`;
        }
    }

    styleSelect.addEventListener('change', updateGeneratedPrompt);
    subjectSelect.addEventListener('change', updateGeneratedPrompt);
    detailsSelect.addEventListener('change', updateGeneratedPrompt);
    settingSelect.addEventListener('change', updateGeneratedPrompt);

    // Initial call to set the default prompt text
    updateGeneratedPrompt();

    // Loading Indicator Logic
    window.addEventListener('load', () => {
        const loadingIndicator = document.getElementById('loading');
        loadingIndicator.style.display = 'none'; // Hide loading spinner once everything is loaded
    });
}); 