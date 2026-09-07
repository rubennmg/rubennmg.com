export type Locale = "es" | "en";

export const socials = [
    {
        label: "GitHub",
        href: "https://github.com/rubennmg",
        icon: "/github.svg",
    },
    {
        label: "LinkedIn",
        href: "https://www.linkedin.com/in/rubennmg",
        icon: "/linkedin.svg",
    },
];

const shared = {
    profile: {
        name: "Rubén Martínez Ginzo",
        handle: "rubennmg",
        location: "Asturias, España",
        email: "martinezginzoruben@gmail.com",
    },
    skills: [
        ".NET",
        "C/C++",
        "Python",
        "Ruby on Rails",
        "Node.js",
        "FastAPI",
        "Java",
        "Astro",
        "SQL",
        "Docker",
        "GitHub Actions",
    ],
};

export const portfolio = {
    es: {
        locale: "es" as const,
        meta: {
            title: "Rubén Martínez Ginzo | Ingeniero informático",
            description:
                "Experiencia, formación y proyectos de Rubén Martínez Ginzo, ingeniero informático en Asturias.",
        },
        profile: {
            ...shared.profile,
            role: "Ingeniero informático · Desarrollador de software",
            intro: "Ingeniería de software con criterio",
            summary:
                "Ingeniero informático con experiencia profesional desde 2024 en proyectos que abarcan producto, backend, frontend e infraestructura. Enfoque práctico, orientado a comprender cada problema y construir soluciones mantenibles.",
        },
        navigation: [
            { label: "Experiencia", href: "#experiencia" },
            { label: "Formación", href: "#formacion" },
            { label: "Proyectos", href: "#proyectos" },
            { label: "Juegos", href: "/games/catan" },
        ],
        hero: {
            primaryAction: "Ver experiencia",
            secondaryAction: "LinkedIn",
            status: "Actualmente",
            statement: "Desarrollador de software en Futuver",
        },
        highlights: [
            { value: "2024 — hoy", label: "Experiencia profesional" },
            { value: "Asturias", label: "España" },
        ],
        sections: {
            experience: {
                id: "experiencia",
                eyebrow: "01 · Trayectoria",
                title: "Experiencia profesional",
                description:
                    "Experiencia desarrollada de forma continua en equipos de software y productos con necesidades concretas.",
            },
            education: {
                id: "formacion",
                eyebrow: "02 · Formación",
                title: "Formación",
                description:
                    "Formación académica en ingeniería informática, tecnologías de la información y gestión de sistemas software.",
            },
            projects: {
                id: "proyectos",
                eyebrow: "03 · Proyectos",
                title: "Proyectos seleccionados",
                description:
                    "Selección de proyectos académicos y personales desarrollados con distintas tecnologías, arquitecturas y enfoques de resolución.",
            },
            contact: {
                id: "contacto",
                eyebrow: "04 · Contacto",
                title: "Contacto profesional",
                description:
                    "Para consultas profesionales o información adicional, están disponibles el correo electrónico y los perfiles públicos.",
            },
        },
        experience: [
            {
                title: "Desarrollador de software",
                place: "Futuver",
                date: "abr. 2025 — actualidad",
                description:
                    "Desarrollo y evolución de soluciones de software en un entorno profesional, atendiendo a requisitos de negocio, mantenibilidad y calidad técnica.",
                link: "https://futuver.com/",
                logo: "/futu_logo.jpg",
                current: true,
            },
            {
                title: "Desarrollador de software · Prácticas",
                place: "Futuver",
                date: "oct. 2024 — mar. 2025",
                description:
                    "Primera etapa en la compañía, enfocada en consolidar procesos de desarrollo profesional, trabajo en equipo y entrega de funcionalidad.",
                link: "https://futuver.com/",
                logo: "/futu_logo.jpg",
            },
            {
                title: "Desarrollador full stack · Prácticas",
                place: "Neosystems",
                date: "feb. 2024 — ago. 2024",
                description:
                    "Desarrollo de aplicaciones web conectando interfaz, lógica de negocio y persistencia, dentro de un equipo y un producto existentes.",
                link: "https://neosystems.es/",
                logo: "/neosystems_logo.jpeg",
            },
        ],
        education: [
            {
                title: "Máster en Ingeniería Informática",
                place: "Universidad de Oviedo",
                date: "sept. 2024 — 2026",
                description:
                    "Máster finalizado, con formación avanzada en tecnologías de la información, arquitectura, gestión y desarrollo de sistemas software.",
                link: "https://www.uniovi.es",
            },
            {
                title: "Grado en Ingeniería Informática en TI",
                place: "Universidad de Oviedo",
                date: "sept. 2020 — jun. 2024",
                description:
                    "Base técnica en ingeniería del software, bases de datos, redes, sistemas y desarrollo de aplicaciones.",
                link: "https://www.uniovi.es",
            },
            {
                title: "Bachillerato tecnológico",
                place: "IES Jovellanos",
                date: "sept. 2018 — jun. 2020",
                description:
                    "Itinerario tecnológico previo a la formación universitaria en ingeniería informática.",
                link: "https://www.iesjovellanos.com",
            },
        ],
        projects: [
            {
                title: "Procesamiento RAW en tiempo real",
                kicker: "Trabajo Fin de Máster · 2026",
                description:
                    "Aplicación interactiva para mejorar el contraste de imágenes en formato crudo y diseñar perfiles de procesamiento exportables a flujos acelerados en tiempo real.",
                points: [
                    "Pipeline configurable de revelado, debayerizado y realce de contraste.",
                    "Interfaz de escritorio para comparar operaciones y ajustar parámetros visualmente.",
                    "Implementación y evaluación de operaciones sobre CPU y GPU.",
                ],
                link: "https://github.com/rubennmg/TFM",
                monogram: "TFM",
                images: [
                    {
                        src: "/TFM/TFM-1.webp",
                        alt: "Interfaz del TFM con un flujo de procesado aplicado a una fotografía de bosque",
                    },
                    {
                        src: "/TFM/TFM-2.webp",
                        alt: "Interfaz del TFM procesando una imagen RAW nocturna",
                    },
                    {
                        src: "/TFM/TFM-3.webp",
                        alt: "Resultados del benchmark de operaciones de imagen sobre CPU y GPU",
                    },
                ],
                tags: ["Python", "PyTorch", "PyQt", "Procesamiento RAW"],
            },
            {
                title: "WhatTheNoise",
                kicker: "Trabajo Fin de Grado · 2024",
                description:
                    "Sistema para detectar eventos acústicos en entornos físicos, estimar el origen del sonido mediante dos micrófonos y registrar información útil para su posterior clasificación.",
                points: [
                    "Localización aproximada mediante diferencia temporal de llegada (TDOA).",
                    "Detección y registro de sonidos continuos, móviles y puntuales.",
                    "Prototipo sobre Raspberry Pi con configuración desde una interfaz web.",
                ],
                link: "https://github.com/rubennmg/WhatTheNoise",
                monogram: "WTN",
                images: [
                    {
                        src: "/TFG/WTN-1.webp",
                        alt: "Arquitectura de WhatTheNoise con Raspberry Pi y dos micrófonos",
                    },
                    {
                        src: "/TFG/WTN-2.webp",
                        alt: "Pantalla de inicio de la aplicación web WhatTheNoise",
                    },
                    {
                        src: "/TFG/WTN-3.webp",
                        alt: "Pantalla de grabación en curso de WhatTheNoise",
                    },
                ],
                tags: ["Python", "C/C++", "Flask", "Raspberry Pi"],
            },
            {
                title: "rubennmg.com",
                kicker: "Portfolio y laboratorio personal",
                description:
                    "Portfolio en Astro dentro de una arquitectura full stack con FastAPI y PostgreSQL, preparada para rankings de juegos y nuevas herramientas.",
                link: "https://github.com/rubennmg/rubennmg.com",
                liveLink: "/games/catan",
                liveLabel: "Explorar Catán",
                image: "/appLogo.svg",
                tags: ["Astro", "FastAPI", "PostgreSQL", "Docker"],
            },
            {
                title: "SI2022-PL41",
                kicker: "Proyecto académico",
                description:
                    "Aplicación de escritorio para la gestión ficticia del COIIPA, desarrollada con Java, Ruby y Maven.",
                link: "https://github.com/miermontoto/SI2022-PL41",
                image: "/coiipa.png",
                tags: ["Java", "Ruby", "Maven"],
            },
        ],
        labels: {
            current: "En curso",
            code: "Ver código",
            email: "Contactar por email",
            theme: "Cambiar tema",
            language: "View in English",
            languageShort: "EN",
            madeWith: "Construido con Astro",
            updated: "Actualizado en",
            skip: "Saltar al contenido",
            portraitAlt: "Retrato de Rubén Martínez Ginzo",
            carousel: {
                label: "Galería del proyecto",
                previous: "Imagen anterior",
                next: "Imagen siguiente",
                goTo: "Mostrar imagen",
                pause: "Pausar reproducción automática",
                play: "Reanudar reproducción automática",
                expand: "Ampliar imagen",
                close: "Cerrar imagen ampliada",
            },
        },
        skills: shared.skills,
        socials,
    },
    en: {
        locale: "en" as const,
        meta: {
            title: "Rubén Martínez Ginzo | Software engineer",
            description:
                "Experience, education and selected work by Rubén Martínez Ginzo, a software engineer based in Asturias, Spain.",
        },
        profile: {
            ...shared.profile,
            location: "Asturias, Spain",
            role: "Software engineer · Software developer",
            intro: "Software engineering with sound judgement",
            summary:
                "Software engineer with professional experience since 2024 across product, backend, frontend and infrastructure. A practical approach focused on understanding each problem and delivering maintainable solutions.",
        },
        navigation: [
            { label: "Experience", href: "#experience" },
            { label: "Education", href: "#education" },
            { label: "Projects", href: "#projects" },
            { label: "Games", href: "/games/catan" },
        ],
        hero: {
            primaryAction: "View experience",
            secondaryAction: "LinkedIn",
            status: "Currently",
            statement: "Software developer at Futuver",
        },
        highlights: [
            { value: "2024 — now", label: "Professional experience" },
            { value: "Asturias", label: "Spain" },
        ],
        sections: {
            experience: {
                id: "experience",
                eyebrow: "01 · Career",
                title: "Professional experience",
                description:
                    "Continuous experience across software teams and products built around concrete requirements.",
            },
            education: {
                id: "education",
                eyebrow: "02 · Education",
                title: "Education",
                description:
                    "Academic training in computer engineering, information technology and software systems management.",
            },
            projects: {
                id: "projects",
                eyebrow: "03 · Projects",
                title: "Selected projects",
                description:
                    "A selection of academic and personal projects developed with different technologies, architectures and problem-solving approaches.",
            },
            contact: {
                id: "contact",
                eyebrow: "04 · Contact",
                title: "Professional contact",
                description:
                    "For professional enquiries or further information, email and public profiles are available below.",
            },
        },
        experience: [
            {
                title: "Software developer",
                place: "Futuver",
                date: "Apr 2025 — present",
                description:
                    "Development and evolution of software solutions in a professional environment, balancing business requirements, maintainability and technical quality.",
                link: "https://futuver.com/",
                logo: "/futu_logo.jpg",
                current: true,
            },
            {
                title: "Software developer · Internship",
                place: "Futuver",
                date: "Oct 2024 — Mar 2025",
                description:
                    "First stage at the company, focused on professional development processes, teamwork and shipping functionality.",
                link: "https://futuver.com/",
                logo: "/futu_logo.jpg",
            },
            {
                title: "Full-stack developer · Internship",
                place: "Neosystems",
                date: "Feb 2024 — Aug 2024",
                description:
                    "Web application development connecting interfaces, business logic and persistence within an existing team and product.",
                link: "https://neosystems.es/",
                logo: "/neosystems_logo.jpeg",
            },
        ],
        education: [
            {
                title: "Master's in Computer Engineering",
                place: "University of Oviedo",
                date: "Sep 2024 — 2026",
                description:
                    "Completed Master's degree with advanced studies in information technology, architecture, management and software systems development.",
                link: "https://www.uniovi.es",
            },
            {
                title: "BSc in Computer Engineering — IT",
                place: "University of Oviedo",
                date: "Sep 2020 — Jun 2024",
                description:
                    "Technical foundations in software engineering, databases, networks, systems and application development.",
                link: "https://www.uniovi.es",
            },
            {
                title: "Technology-focused secondary education",
                place: "IES Jovellanos",
                date: "Sep 2018 — Jun 2020",
                description:
                    "Technology-focused studies prior to university-level computer engineering.",
                link: "https://www.iesjovellanos.com",
            },
        ],
        projects: [
            {
                title: "Real-time RAW image processing",
                kicker: "Master's thesis · 2026",
                description:
                    "An interactive application for enhancing the contrast of RAW images and designing processing profiles that can be exported to accelerated real-time pipelines.",
                points: [
                    "Configurable development, debayering and contrast-enhancement pipeline.",
                    "Desktop interface for comparing operations and adjusting parameters visually.",
                    "Implementation and performance evaluation of operations on CPU and GPU.",
                ],
                link: "https://github.com/rubennmg/TFM",
                monogram: "TFM",
                images: [
                    {
                        src: "/TFM/TFM-1.webp",
                        alt: "Master's thesis interface with a processing pipeline applied to a forest photograph",
                    },
                    {
                        src: "/TFM/TFM-2.webp",
                        alt: "Master's thesis interface processing a night-time RAW image",
                    },
                    {
                        src: "/TFM/TFM-3.webp",
                        alt: "CPU and GPU image-operation benchmark results",
                    },
                ],
                tags: ["Python", "PyTorch", "PyQt", "RAW processing"],
            },
            {
                title: "WhatTheNoise",
                kicker: "Bachelor's thesis · 2024",
                description:
                    "A system for detecting acoustic events in physical environments, estimating their source with two microphones and recording useful data for subsequent classification.",
                points: [
                    "Approximate source localisation using time difference of arrival (TDOA).",
                    "Detection and recording of continuous, moving and transient sounds.",
                    "Raspberry Pi prototype with configuration through a web interface.",
                ],
                link: "https://github.com/rubennmg/WhatTheNoise",
                monogram: "WTN",
                images: [
                    {
                        src: "/TFG/WTN-1.webp",
                        alt: "WhatTheNoise architecture with a Raspberry Pi and two microphones",
                    },
                    {
                        src: "/TFG/WTN-2.webp",
                        alt: "WhatTheNoise web application home screen",
                    },
                    {
                        src: "/TFG/WTN-3.webp",
                        alt: "WhatTheNoise recording-in-progress screen",
                    },
                ],
                tags: ["Python", "C/C++", "Flask", "Raspberry Pi"],
            },
            {
                title: "rubennmg.com",
                kicker: "Portfolio and personal lab",
                description:
                    "An Astro portfolio within a full-stack FastAPI and PostgreSQL architecture, prepared for game rankings and new tools.",
                link: "https://github.com/rubennmg/rubennmg.com",
                liveLink: "/games/catan",
                liveLabel: "Explore Catan",
                image: "/appLogo.svg",
                tags: ["Astro", "FastAPI", "PostgreSQL", "Docker"],
            },
            {
                title: "SI2022-PL41",
                kicker: "Academic project",
                description:
                    "A desktop application for the fictional management of COIIPA, built with Java, Ruby and Maven.",
                link: "https://github.com/miermontoto/SI2022-PL41",
                image: "/coiipa.png",
                tags: ["Java", "Ruby", "Maven"],
            },
        ],
        labels: {
            current: "In progress",
            code: "View code",
            email: "Contact by email",
            theme: "Change theme",
            language: "Ver en español",
            languageShort: "ES",
            madeWith: "Built with Astro",
            updated: "Updated",
            skip: "Skip to content",
            portraitAlt: "Portrait of Rubén Martínez Ginzo",
            carousel: {
                label: "Project gallery",
                previous: "Previous image",
                next: "Next image",
                goTo: "Show image",
                pause: "Pause automatic playback",
                play: "Resume automatic playback",
                expand: "Enlarge image",
                close: "Close enlarged image",
            },
        },
        skills: shared.skills,
        socials,
    },
};

export type PortfolioContent = (typeof portfolio)[Locale];
